import json,sys,os

with open('run_response.json','r',encoding='utf-8-sig') as f:
    r=json.load(f)
raw=r.get('result',{}).get('raw',{})
thread_id=raw.get('thread_id')
run_id=raw.get('id')
print('thread_id=',thread_id)
print('run_id=',run_id)
if not thread_id or not run_id:
    print('No thread/run id found, exiting')
    sys.exit(1)
# Try to import AssistantsAgent and poll
try:
    from assistants_agent import AssistantsAgent
except Exception as e:
    print('Could not import AssistantsAgent:',e)
    sys.exit(2)
# Ensure OPENAI_API_KEY
if not os.getenv('OPENAI_API_KEY'):
    print('OPENAI_API_KEY not set; cannot poll remote run.'); sys.exit(3)
agent=AssistantsAgent()
print('Polling run completion via OpenAI API...')
run=agent.wait_for_run_completion(thread_id, run_id, poll_interval=2.0, max_wait_seconds=60)
try:
    out = run
    # convert to json-friendly dict if possible
    if hasattr(run, 'to_dict'):
        out = run.to_dict()
    else:
        try:
            out = json.loads(json.dumps(run, default=lambda o: getattr(o,'__dict__', str(o))))
        except Exception:
            out = str(run)
except Exception:
    out = str(run)
with open('run_final.json','w',encoding='utf8') as f:
    if isinstance(out, str):
        f.write(out)
    else:
        json.dump(out,f,indent=2)
print('Wrote run_final.json')
print('Final status:', getattr(run,'status',None))
