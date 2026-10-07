// Optional builder: requires a host-provided @oai/artifact-tool.
// Creates native, editable evidence pages. No private or external assets.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';

const here = path.dirname(fileURLToPath(import.meta.url));
export const gallery = JSON.parse(await fs.readFile(path.join(here, 'gallery.json'), 'utf8'));
const source = JSON.parse(await fs.readFile(path.join(here, gallery.source), 'utf8'));
if (!gallery.synthetic || !source.synthetic) throw new Error('Only synthetic fixtures are supported.');
const [baseline, compact, large] = source.rows;
const delta = (compact.accuracy - baseline.accuracy).toFixed(1);
const saved = baseline.latency - compact.latency;
const percent = (saved / baseline.latency * 100).toFixed(1);
const blue = {ink:'#343A40', muted:'#606B74', primary:'#0B6FCA', pale:'#EFF6FC', line:'#DCE3E8', bg:'#FFFFFF'};
const wine = {ink:'#1F2430', muted:'#666A73', primary:'#7D1E2F', pale:'#FAE9EC', line:'#D9DCE3', bg:'#FFFFFF'};
const dark = {ink:'#E7E9EA', muted:'#A5AFB2', primary:'#E7E9EA', pale:'#1B313A', line:'#435760', bg:'radial(#173F4B 0%, #071F29 48%, #01080C 100%)'};
const green = {ink:'#171A18', muted:'#5F6763', primary:'#008C63', pale:'#E5F6F1', line:'#CEDBD6', bg:'#FFFFFF'};
const dual = {ink:'#252525', muted:'#62676E', primary:'#284B7D', pale:'#EDF2F8', line:'#D8DADD', bg:'#FFFFFF'};
const neutral = {ink:'#222222', muted:'#707070', primary:'#222222', pale:'#F4F4F4', line:'#D0D0D0', bg:'#FFFFFF'};
const report = {ink:'#27242A', muted:'#656068', primary:'#96324A', pale:'#FAEFF2', line:'#E2DADF', bg:'#FFFFFF'};

export async function buildPage(item, font = 'Arial') {
  const p = Presentation.create({slideSize:{width:item.width, height:item.height}});
  const s = p.slides.add();
  const theme = item.id.includes('wine') ? wine : item.id.includes('dark') ? dark : item.id === 'project-green' ? green : item.id.includes('dual') ? dual : item.id.includes('neutral') ? neutral : item.id.includes('dense') ? report : blue;
  s.background.fill = theme.bg;
  function text(value,x,y,w,h,size=26,color=theme.ink,bold=false,family=font) {
    const shape=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
    shape.text=value;
    shape.text.style={typeface:family,fontSize:size,color,bold,autoFit:'none'};
    return shape;
  }
  function rect(x,y,w,h,fill,line='none',radius=0) {
    return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:line==='none'?0:1},borderRadius:radius});
  }
  function rule(x,y,w,color=theme.line) {return s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},fill:'none',line:{fill:color,width:1}});}
  function table(x,y,w,h,options={}) {
    const values=[['Setting','Accuracy (%)','Latency (ms)'],...source.rows.map(r=>[r.name,r.accuracy.toFixed(1),String(r.latency)])];
    const t=s.tables.add({rows:4,columns:3,left:x,top:y,width:w,height:h,columnWidths:[w*.44,w*.28,w*.28],values});
    const quietBorder={fill:options.surface??'#FFFFFF',width:0.1};
    t.borders.outside=quietBorder;
    t.borders.inside=quietBorder;
    t.cells.block({row:0,column:0,rowCount:4,columnCount:3}).assign({fill:options.surface??theme.bg,textStyle:{typeface:font,fontSize:options.size??25,color:theme.ink},margins:{left:18,right:14,top:16,bottom:12}});
    t.cells.block({row:0,column:0,rowCount:1,columnCount:3}).assign({fill:options.surface??theme.pale,textStyle:{typeface:font,fontSize:(options.size??25)-2,color:theme.primary,bold:true}});
    t.cells.block({row:2,column:0,rowCount:1,columnCount:3}).assign({fill:options.surface??theme.pale,textStyle:{typeface:font,fontSize:options.size??25,color:theme.primary,bold:true}});
    for(let row=1;row<4;row++) rule(x+18,y+row*h/4,w-36);
    return t;
  }
  function node(label,x,y,w,h,focus=false) {
    const n=rect(x,y,w,h,focus?theme.pale:'#FFFFFF',focus?theme.primary:theme.line,8);
    text(label,x+18,y+20,w-36,h-30,27,focus?theme.primary:theme.ink,focus);
    return n;
  }
  function connect(a,b,from='right',to='left') {
    s.shapes.connect(a,b,{kind:'straight',fromSide:from,toSide:to,line:{style:'solid',fill:theme.primary,width:2},tail:{type:'arrow',width:'med',length:'med'}});
  }
  const dense=item.id==='dense-reading-report';
  const left=item.id.includes('dual')?88:64;
  text(item.name_en.toUpperCase(),left,30,item.width-128,26,15,theme.muted,true);
  text(item.title,left,77,item.width-left-64,112,dense?43:41,theme.primary,true);
  const footY=item.height-48;
  rule(left,footY-16,item.width-left-64);
  text('SYNTHETIC TEACHING DATA  /  candidate-filter-fixture-v1  /  No real benchmark claim',left,footY,item.width-left-64,27,15,theme.muted);
  s.speakerNotes.textFrame.setText(`[slide-id:S01] [role:main]\nPreset: ${item.id}; cards: ${item.cards.join(' + ')}.\nSource: ../synthetic-study/source.json (${source.id}). All values are invented teaching data. One content-page example, not evidence of full-deck narrative validation.`);

  if(item.id==='author-light') {
    text(`+${delta} pp`,64,202,440,105,80,theme.primary,true);
    text('Accuracy vs. baseline',68,318,420,42,26);
    text(`${saved} ms less`,663,202,550,105,80,theme.ink,true);
    text('Time per query vs. baseline',666,318,540,42,26);
    table(64,389,1152,234,{size:24});
  } else if(item.id==='academic-oral-wine') {
    text('Accuracy gains and latency costs must be read together.',64,175,1152,50,27);
    table(64,246,735,293,{size:25});
    text('Compact to large',850,252,365,46,26,theme.primary,true);
    text('+0.5 pp',850,310,365,76,53,theme.ink,true);
    text('+75 ms / query',850,392,365,64,35,theme.ink,true);
    text('No repeated trials or\nuncertainty estimates.',850,472,350,74,24,theme.muted);
    rect(64,565,1152,62,theme.pale);
    text('The fixture supports a trade-off, not a general scaling claim.',84,580,1112,41,26,theme.primary,true);
    text('Source: original synthetic fixture, rows 2–3. No external paper or experiment.',64,630,1152,20,16,'#0077CC');
  } else if(item.id==='experiment-review') {
    text('Latency per query (ms); smaller is better',64,185,840,40,26);
    s.charts.add('bar',{position:{left:64,top:238,width:1152,height:330},categories:source.rows.map(r=>r.name),series:[{name:'Latency (ms)',values:source.rows.map(r=>r.latency),fill:'#91C5F0',points:[{idx:1,fill:theme.primary}],line:{fill:'none',width:0}}],barOptions:{direction:'column',grouping:'clustered',gapWidth:85},hasLegend:false,xAxis:{visible:true,textStyle:{typeface:font,fontSize:25,fill:theme.ink},majorGridlines:null},yAxis:{visible:true,min:0,max:180,majorUnit:60,numberFormatCode:'0',textStyle:{typeface:font,fontSize:21,fill:theme.muted},majorGridlines:{fill:theme.line,width:1}},dataLabels:{showValue:true,position:'outEnd',textStyle:{typeface:font,fontSize:27,fill:theme.ink,bold:true}},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF'});
    text(`${baseline.latency} − ${compact.latency} = ${saved} ms`,64,591,570,55,33,theme.primary,true);
    text(`Accuracy: ${baseline.accuracy.toFixed(1)}% baseline, ${compact.accuracy.toFixed(1)}% compact`,647,595,566,50,25);
  } else if(item.id==='technical-review-light') {
    text('Conceptual data path. The fixture does not measure internal stage costs.',64,183,1152,64,25,theme.muted);
    const a=node('Query',64,329,196,114);
    const b=node('Candidate\nfilter',330,302,260,168,true);
    const c=node('Ranker',669,329,226,114);
    const d=node('Top result',977,329,239,114);
    connect(a,b);connect(b,c);connect(c,d);
    text('Select a subset',344,502,260,45,24,theme.primary,true);
    text('Order that subset',674,502,300,45,24);
    rule(64,568,1152);
    text('A ranker cannot recover candidates that the filter has removed.',64,596,1152,54,29,theme.ink,true);
  } else if(item.id==='technical-review-dark') {
    text('Compact filter',64,224,430,50,28,theme.muted);
    text(`${compact.accuracy.toFixed(1)}%`,58,290,430,124,95,theme.ink,true);
    text(`${compact.latency} ms per query`,64,427,390,50,30,theme.ink);
    text('Fixture comparison only.\nNo deployment validation.',64,518,400,87,24,theme.muted);
    table(520,222,696,350,{size:25,surface:theme.pale});
    text('Higher accuracy and lower latency than baseline',539,599,677,47,23,theme.ink,true);
  } else if(item.id==='project-green') {
    rule(64,63,1152,theme.primary);
    text('Illustrative review plan, not an actual project status report',64,180,1152,46,25,theme.muted);
    const milestones=[['01','Fixture','Values specified'],['02','Comparison','Deltas checked'],['03','Repeatability','Measurements needed'],['04','Deployment','Conditions unknown']];
    milestones.forEach((m,i)=>{const x=64+i*295;text(m[0],x,262,215,66,47,i===2?theme.primary:theme.muted,true);rule(x,342,253,i===2?theme.primary:theme.line);text(m[1],x,368,270,52,28,theme.ink,true);text(m[2],x,430,260,76,24,i===2?theme.primary:theme.muted);});
    rect(64,548,1152,83,theme.pale,'none',10);
    text('Next evidence: repeated trials under stated hardware and workload conditions.',85,568,1108,60,28,theme.ink,true);
  } else if(item.id==='project-summary-dual-semantics') {
    rect(28,30,8,627,theme.primary);
    text('Fixture evidence',88,207,600,49,28,theme.primary,true);
    text('Next evidence',866,207,340,49,28,theme.ink,true);
    rect(866,263,176,6,'#E8CDA9');
    table(88,276,707,270,{size:24});
    text('Repeated measurements\n\nHardware and workload\n\nMemory and candidate recall',866,297,350,280,24,theme.ink);
    text(`Compact vs. baseline: +${delta} pp, ${saved} ms less`,88,584,1080,53,30,theme.primary,true);
  } else if(item.id==='neutral-evidence-review') {
    text('Source excerpt',64,207,710,42,22,theme.muted,true);
    rect(64,270,700,314,theme.pale);
    text('"synthetic": true,\n"unmeasured": [\n  "Repeatability",\n  "Hardware and workload variation",\n  "Memory use",\n  "Candidate recall"\n]',87,294,654,274,23,theme.ink,false,'Courier New');
    text('No error bars',823,277,380,47,30,theme.ink,true);
    text('No repeated measurements\nto estimate uncertainty.',823,337,380,80,26);
    text('No deployment claim',823,443,390,47,30,theme.ink,true);
    text('The source explicitly excludes\na real evaluation setup.',823,504,390,83,26);
    text('Four unmeasured conditions limit the interpretation.',64,608,1152,48,27,theme.ink,true);
  } else {
    text('Research note 01    /    Independent reading    /    Original teaching fixture',64,166,1272,42,21,theme.muted);
    text('The compact setting combines a 2.0 percentage-point accuracy gain with 35 ms lower latency.\nThese invented values illustrate a comparison method; they do not establish real performance.',64,226,1272,94,27,theme.ink);
    table(64,349,797,288,{size:25});
    text('How to read the difference',928,344,408,49,27,theme.primary,true);
    text('Accuracy is a percentage of\ncorrect top results. Subtracting\n86.0% and 84.0% gives 2.0\npercentage points, not 2.0%.',928,412,408,151,24);
    text('35 / 120 ≈ 29.2%',928,592,408,49,32,theme.primary,true);
    text('relative latency reduction',928,644,408,40,23,theme.muted);
    rule(64,681,797);
    text('Mechanism and scope',64,710,797,42,28,theme.primary,true);
    text('Query → candidate filter → ranker → top result',64,768,797,46,28,theme.ink,true);
    text('Filtering determines which candidates reach the ranker.\nThe fixture does not measure candidate recall or stage costs.',64,825,797,73,24);
    text('Still unmeasured',928,722,408,44,27,theme.primary,true);
    text('Repeatability\nHardware and workload variation\nMemory use\nCandidate recall',928,781,408,129,23);
  }
  return p;
}

if(process.argv[1] && import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href) {
  if(!process.argv[2]) throw new Error('Usage: node build_gallery.mjs /path/to/new-output-directory');
  const out=path.resolve(process.argv[2]);
  await fs.mkdir(out); // Refuse to overwrite an existing gallery.
  for(const item of gallery.items) {
    const p=await buildPage(item);
    await (await PresentationFile.exportPptx(p)).save(path.join(out,`${item.id}.pptx`));
    const png=await p.export({slide:p.slides.items[0],format:'png',scale:1.5});
    await fs.writeFile(path.join(out,`${item.id}.png`),new Uint8Array(await png.arrayBuffer()));
  }
  console.log('Draft gallery exported. Inspect every page before publication.');
}
