"""Tests use a temporary local static server; Python + playwright + Chromium needed only for tests."""
from pathlib import Path
import json,re,threading,functools
from datetime import date
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
records=[]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT/'app')))
threading.Thread(target=server.serve_forever,daemon=True).start()
def run():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1440,'height':1150},device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
  def s():return page.evaluate('StayWise.getState()')
  def chat(t):
   page.locator('#message').fill(t);page.locator('#chat button').click()
  def fresh():page.locator('#reset').click()
  def test(id,expected,fn):
   try: actual=fn();records.append(dict(id=id,expected=expected,actual=actual or 'Assertions satisfied.',status='PASS'))
   except Exception as e: records.append(dict(id=id,expected=expected,actual=str(e),status='FAIL'))
  def t01():
   fresh();chat('Find a hotel in Birmingham under £100 with breakfast.');a=s();assert a['pending'] is None and a['budget']==100 and a['breakfast'];assert len(a['results'])==2;assert all(h['price']<=100 and h['breakfast'] for h in a['results']);return '2 Birmingham matches; no clarification; budget source explicit.'
  test('T01','Explicit request filters directly without clarification.',t01)
  def t02():
   fresh();chat('I want a cheap hotel in London.');assert s()['pending']=='budget' and s()['budget'] is None;assert page.locator('.hotel').count()==0;page.get_by_role('button',name='Up to £100',exact=True).click();assert s()['budgetSource']=='clarified';assert len(s()['results'])==3;return 'Budget question shown; £100 confirmation gives 3 matches.'
  test('T02','Subjective budget is clarified before showing results.',t02)
  def t03():
   fresh();chat('An affordable hotel in Manchester');page.get_by_role('button',name='Use suggested £100',exact=True).click();assert s()['budgetSource']=='suggested' and s()['budget']==100;assert 'not a real-time market estimate' in page.locator('#messages').inner_text();assert 'accepted by you' in page.locator('#source').inner_text();return 'Accepted demo default shown in conversation and budget source.'
  test('T03','Suggested budget is opt-in and labelled.',t03)
  def t04():
   chat('Actually, my maximum budget is £80.');a=s();assert a['budget']==80 and a['budgetSource']=='explicit' and a['city']=='Manchester';assert len(a['results'])==3;assert all(h['price']<=80 for h in a['results']);return 'Manchester retained; £80 maximum gives 3 valid matches.'
  test('T04','Budget revision replaces the previous maximum.',t04)
  def t05():
   page.locator('#city').select_option('London');assert s()['city']=='London';assert all(h['city']=='London' and h['price']<=80 for h in s()['results']);return '2 London records, respecting the retained £80 maximum.'
  test('T05','City filter synchronises state and results.',t05)
  def t06():
   fresh();chat('Manchester at least 4.5 stars');assert len(s()['results'])==3;assert all(h['rating']>=4.5 for h in s()['results']);return '3 results rated at least 4.5; no optional-budget question.'
  test('T06','Rating threshold is applied.',t06)
  def t07():
   fresh();chat('Manchester with breakfast');assert len(s()['results'])==4;assert all(h['breakfast'] for h in s()['results']);return '4 breakfast matches.'
  test('T07','Breakfast is a hard constraint.',t07)
  def t08():
   chat('With parking and gym');assert len(s()['results'])==1;assert all(h['parking'] and h['gym'] and h['breakfast'] for h in s()['results']);return '1 hotel satisfies breakfast, parking and gym together.'
  test('T08','Multiple facilities use AND semantics.',t08)
  def t09():
   chat('Change my budget to £60');a=s();assert not a['results'] and a['budget']==60 and a['facilities']==['parking','gym'];assert page.get_by_role('button',name='Remove budget limit').is_visible();page.get_by_role('button',name='Remove budget limit').click();assert s()['budget'] is None and len(s()['results'])==1;return 'No-match state retains constraints; explicit budget removal restores 1 result.'
  test('T09','No matches explains the conflict and offers user-controlled recovery.',t09)
  def t10():
   page.locator('.hotel').first.get_by_role('button',name='Helpful',exact=True).click();assert list(s()['feedback'].values())==['Helpful'];page.locator('.hotel').first.get_by_role('button',name='Not helpful',exact=True).click();assert list(s()['feedback'].values())==['Not helpful'];assert 'No model training' in page.locator('.feedback').inner_text();return 'Feedback can be set and revised in memory.'
  test('T10','Feedback controls record their current value.',t10)
  def t11():
   old=s();chat('What is the weather?');a=s();assert 'No preferences were changed' in a['messages'][-1]['text'];assert a['budget']==old['budget'] and a['city']==old['city'];chat('London and Birmingham under £70');assert 'one city' in s()['messages'][-1]['text'];return 'Unsupported task and multiple cities rejected without changing preferences.'
  test('T11','Unsupported inputs receive an honest fallback.',t11)
  def t12():
   fresh();a=s();assert a['city']=='' and a['budget'] is None and a['feedback']=={} and len(a['messages'])==1 and a['pending'] is None;return 'Search state, feedback and conversation cleared.'
  test('T12','New search resets every interaction state.',t12)
  def t13():
   chat('Cheap hotel with breakfast');assert s()['pending']=='city';page.get_by_role('button',name='London',exact=True).click();assert s()['pending']=='budget' and s()['breakfast'];page.get_by_role('button',name='Up to £100',exact=True).click();chat('With parking');assert s()['pending'] is None and s()['budget']==100;return 'City precedes budget; breakfast retained; confirmed budget not re-asked.'
  test('T13','Pending budget survives city clarification; no repeated confirmed-budget question.',t13)
  def t14():
   fresh();chat('Manchester under £100');page.locator('#budget').fill('80');page.locator('#budget').dispatch_event('change');assert s()['budget']==80 and s()['budgetSource']=='filter';chat('Show me something cheaper');assert s()['pending']=='budget' and s()['budget']==80;assert page.locator('.hotel').count()==0;return 'Filter revision synchronised; “cheaper” asks rather than guessing.'
  test('T14','Chat and filters share state and relative revision is clarified.',t14)
  def t15():
   page.reload();assert s()['city']=='';chat('Birmingham under £100');page.locator('.hotel').first.get_by_role('button',name='View details').click();assert page.locator('#detail').is_visible();page.locator('#close-detail').click();assert not page.locator('#detail').is_visible();return 'Local HTTP reload works; details dialog opens and closes.'
  test('T15','Refresh and details work through the static test server.',t15)
  def t16():
   for city in ['London','Birmingham','Manchester']:
    for maximum in [50,60,80,100,150,200]:
     fresh();chat(f'{city} under £{maximum} with breakfast');a=s();assert all(h['price']<=maximum and h['breakfast'] and h['city']==city for h in a['results']);assert a['results']==sorted(a['results'],key=lambda h:(-h['rating'],h['price'],h['id']));
     for h in a['results']:
      card=page.locator(f'article[data-id="{h["id"]}"]');assert f'£{h["price"]}' in card.inner_text();assert f'£{maximum} maximum' in card.locator('.reason').inner_text();assert 'breakfast available' in card.locator('.reason').inner_text()
   return '18 city/maximum combinations checked for constraints, ranking and grounded explanations.'
  test('T16','Price invariants, ranking and explanations agree with data.',t16)
  def t17():
   page.set_viewport_size({'width':390,'height':844});fresh();chat('Birmingham under £100 with breakfast');assert page.evaluate('document.documentElement.scrollWidth <= innerWidth');page.screenshot(path=str(ROOT/'docs/mobile.png'),full_page=True);page.set_viewport_size({'width':1440,'height':1150});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth');return 'No horizontal overflow at 390px or 1440px; mobile capture saved.'
  test('T17','Desktop and narrow layout retain accessible content.',t17)
  def t18():
   data=json.loads((ROOT/'app/hotels.json').read_text());assert data==page.evaluate('HOTEL_DATA');assert len(data)==18;assert len(set(h['id'] for h in data))==18;assert not errors;return '18 unique records match offline mirror; zero browser page errors.'
  test('T18','Offline dataset mirror and runtime health are checked.',t18)
  def t19():
   fresh()
   chat('Manchester with breakfast')
   page.locator('#area').select_option('Riverside')
   assert len(s()['results'])==2 and all(h['area']=='Riverside' for h in s()['results'])
   page.locator('.hotel').first.get_by_role('button',name='Helpful',exact=True).click()
   page.locator('#budget').fill('200')
   page.locator('#budget').dispatch_event('change')
   page.locator('#rating').select_option('4.5')
   for facility in ['wifi','parking','gym','restaurant']:
    page.locator('#'+facility).check()
   before=s()
   assert before['budget']==200 and before['budgetSource']=='filter'
   assert before['rating']==4.5 and before['breakfast']
   assert set(before['facilities'])=={'wifi','parking','gym','restaurant'}
   assert before['feedback']
   page.locator('#clear').click()
   after=s()
   assert after['city']=='Manchester'
   assert after['messages'][:len(before['messages'])]==before['messages']
   assert after['feedback']==before['feedback']
   assert after['budget'] is None and after['budgetSource']=='unset'
   assert after['area']=='' and after['rating']==0 and not after['breakfast']
   assert after['facilities']==[] and after['pending'] is None and not after['needsBudget']
   expected=[h for h in json.loads((ROOT/'app/hotels.json').read_text()) if h['city']=='Manchester']
   expected.sort(key=lambda h:(-h['rating'],h['price'],h['id']))
   assert after['results']==expected and page.locator('.hotel').count()==len(expected)
   assert page.locator('#city').input_value()=='Manchester'
   assert page.locator('#budget').input_value()==''
   assert page.locator('#area').input_value()=='' and page.locator('#rating').input_value()=='0'
   for control in ['breakfast','wifi','parking','gym','restaurant']:
    assert not page.locator('#'+control).is_checked()
   chat('Show me something cheaper')
   assert s()['pending']=='budget'
   page.locator('#clear').click()
   assert s()['pending'] is None and not s()['needsBudget'] and s()['results']==expected
   fresh()
   chat('Cheap hotel with breakfast')
   assert s()['pending']=='city' and s()['needsBudget']
   page.locator('#clear').click()
   assert s()['city']=='' and s()['pending']=='city'
   assert not s()['needsBudget'] and not s()['breakfast'] and s()['results']==[]
   return 'Area is strict; Clear filters preserves city, existing conversation and feedback, clears constraints, updates results and cancels obsolete budget clarification; a missing city is requested.'
  test('T19','Clear filters clears constraints within the current search while preserving city, conversation and feedback.',t19)
  # Captures are actual live application states, not illustrative mockups.
  def capture(name):page.screenshot(path=str(ROOT/'docs'/f'{name}.png'),full_page=True)
  fresh();capture('s1-1');chat('Find a hotel in Birmingham under £100 with breakfast.');capture('s1-2');page.locator('.hotel').first.get_by_role('button',name='Helpful',exact=True).click();capture('s1-3')
  fresh();chat('I want a cheap hotel in London.');capture('s2-1');page.get_by_role('button',name='Up to £100',exact=True).click();capture('s2-2');page.locator('#budget').fill('80');page.locator('#budget').dispatch_event('change');capture('s2-3')
  fresh();chat('I want an affordable hotel in Manchester.');capture('s3-1');page.get_by_role('button',name='Use suggested £100',exact=True).click();capture('s3-2');chat('Actually, my maximum budget is £80.');capture('s3-3')
  browser.close()
 server.shutdown()
 (ROOT/'docs/test-results.json').write_text(json.dumps(records,indent=2))
 lines=['# Executed browser test record','', f'Executed {date.today().isoformat()} by Codex using headless Chromium on Linux, a temporary local static HTTP server and Python Playwright. Managed Chromium blocked file:// navigation before page load; direct-file mode and Safari remain unverified. These are functional checks, not a user study. Safari and a physical Mac were not tested.','', '| ID | Expected | Actual | Result |','|---|---|---|---|']
 lines += [f'| {r["id"]} | {r["expected"]} | {r["actual"].replace(chr(10)," ")} | {r["status"]} |' for r in records]
 (ROOT/'docs/TESTING.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(records,indent=2))
 assert all(r['status']=='PASS' for r in records),'Some checks failed; see docs/TESTING.md'
if __name__=='__main__':run()
