import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import {Makers} from '@edgeone/makers-sdk';
const environment=process.argv[2];
if (!['preview','production'].includes(environment)) throw new Error('Expected preview or production');
const token=process.env.EDGEONE_API_TOKEN;
if (!token) throw new Error('EDGEONE_API_TOKEN is required');
const expected=JSON.parse(fs.readFileSync('project.json','utf8'));
const makers=new Makers({token,region:'china'});
const project=await makers.projects.get({projectId:expected.projectId});
if (project.name!==expected.name || project.area!=='mainland') throw new Error('Project identity or region mismatch');
const result=spawnSync(process.execPath,['node_modules/edgeone/edgeone-bin/edgeone.js','makers','deploy','./dist',
  '--name',expected.name,'--env',environment,'--site','china','--skip-ai-gateway-sync','--json'],
  {encoding:'utf8',maxBuffer:10*1024*1024,env:{...process.env,EDGEONE_PAGES_API_TOKEN:token}});
const output=(result.stdout??'')+(result.stderr??'');
console.log(output.replaceAll(token,'[REDACTED]'));
if(result.status!==0) process.exit(result.status??1);
const line=output.split('\n').findLast(x=>x.startsWith('{"status":'));
if (!line) throw new Error('Missing deployment result');
const record=JSON.parse(line);
if(record.status!=='success' || record.projectId!==expected.projectId) throw new Error('Deployment failed or wrong target');
fs.writeFileSync(`.work/${environment}.json`,JSON.stringify(record,null,2));
