// Optional authoring module. Requires a host-provided @oai/artifact-tool.
// Exports drafts only. Finalize, reimport, render and inspect before publishing.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';

const here = path.dirname(fileURLToPath(import.meta.url));
export const manifest = JSON.parse(await fs.readFile(path.join(here, 'comparison.json'), 'utf8'));
export const copy = JSON.parse(await fs.readFile(path.join(here, 'content.json'), 'utf8'));
const fixture = JSON.parse(await fs.readFile(path.resolve(here, manifest.source), 'utf8'));
if (!fixture.synthetic || !manifest.synthetic) throw new Error('Expected synthetic source.');
const [baseline, compact] = fixture.rows;
if ((compact.accuracy - baseline.accuracy).toFixed(1) !== '2.0' || baseline.latency - compact.latency !== 35) {
  throw new Error('Shared copy must be reviewed if the source changes.');
}

const themes = {
  'light-editorial': {primary:'#0B6FCA', ink:'#343A40', muted:'#6B737A', line:'#DCE3E8', pale:'#EFF6FC', bg:'#F7F7F7'},
  'academic-evidence': {primary:'#7D1E2F', ink:'#1F2430', muted:'#666A73', line:'#D9DCE3', pale:'#FAE9EC', bg:'#FFFFFF'},
  'dark-editorial': {primary:'#E7E9EA', ink:'#E7E9EA', muted:'#A5AFB2', line:'#536168', pale:'#1B313A', bg:'radial(#173F4B 0%, #071F29 48%, #01080C 100%)'},
  'green-navigation': {primary:'#008C63', ink:'#171A18', muted:'#5F6763', line:'#CEDBD6', pale:'#E5F6F1', bg:'#FFFFFF'},
  'rail-evidence': {primary:'#284B7D', ink:'#252525', muted:'#666A73', line:'#D8DADD', pale:'#CBD9ED', bg:'#FFFFFF'},
  'neutral-editorial': {primary:'#222222', ink:'#222222', muted:'#707070', line:'#D0D0D0', pale:'#F7F7F7', bg:'#FFFFFF'},
};

export function buildComparison(item, font = 'Arial') {
  const p = Presentation.create({slideSize:manifest.slide_size});
  const c = themes[item.id];
  if (!c) throw new Error(`Unknown display candidate: ${item.id}`);
  const is = id => item.id === id;
  for (let index = 0; index < 2; index++) {
    const s = p.slides.add();
    s.background.fill = c.bg;
    const body = index === 0 ? copy.result : copy.mechanism;
    const label = index === 0 ? 'RESULTS' : 'MECHANISM';
    function text(value, x, y, w, h, size=26, color=c.ink, bold=false) {
      const shape = s.shapes.add({geometry:'textbox', position:{left:x,top:y,width:w,height:h}, fill:'none', line:{fill:'none',width:0}});
      shape.text = value;
      shape.text.style = {typeface:font, fontSize:size, color, bold, autoFit:'none'};
      return shape;
    }
    function rect(x,y,w,h,fill,line='none',radius=0) {
      return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:line==='none'?0:1},borderRadius:radius});
    }
    function rule(x,y,w,color=c.line) {
      s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},fill:'none',line:{fill:color,width:1}});
    }
    function table(x,y,w,h,mode='light') {
      const values=[['Setting','Accuracy (%)','Latency (ms/query)'],...fixture.rows.map(r=>[r.name,r.accuracy.toFixed(1),String(r.latency)])];
      const surface=mode==='dark'?c.pale:'#FFFFFF';
      const t=s.tables.add({rows:4,columns:3,left:x,top:y,width:w,height:h,columnWidths:[w*.40,w*.27,w*.33],values});
      const border={fill:surface,width:0.1};
      t.borders.outside=border;t.borders.inside=border;
      t.cells.block({row:0,column:0,rowCount:4,columnCount:3}).assign({fill:surface,textStyle:{typeface:font,fontSize:25,color:c.ink},margins:{left:16,right:12,top:15,bottom:12}});
      t.cells.block({row:0,column:0,rowCount:1,columnCount:3}).assign({fill:mode==='flat'?surface:c.pale,textStyle:{typeface:font,fontSize:21,color:c.primary,bold:true}});
      t.cells.block({row:2,column:0,rowCount:1,columnCount:3}).assign({fill:mode==='light'?c.pale:surface,textStyle:{typeface:font,fontSize:25,color:c.primary,bold:true}});
      for(let row=1;row<4;row++) rule(x+16,y+row*h/4,w-32);
      return t;
    }
    function flow(x,y,w,vertical=false,flat=false) {
      const gap=vertical?24:34, nw=vertical?w:(w-3*gap)/4, nh=vertical?62:100;
      const nodes=fixture.method.map((label,i)=>{
        const nx=vertical?x:x+i*(nw+gap), ny=vertical?y+i*(nh+gap):y;
        const fill=flat?'none':is('dark-editorial')?c.pale:i===1?c.pale:'#FFFFFF';
        const n=rect(nx,ny,nw,nh,fill,flat?'none':c.line,is('light-editorial')||is('green-navigation')?8:0);
        text(label,nx+12,ny+(vertical?14:31),nw-24,vertical?40:58,vertical?25:24,i===1?c.primary:c.ink,i===1);
        return n;
      });
      for(let i=0;i<3;i++) s.shapes.connect(nodes[i],nodes[i+1],{kind:'straight',fromSide:vertical?'bottom':'right',toSide:vertical?'top':'left',line:{style:'solid',fill:c.primary,width:2},tail:{type:'arrow',width:'med',length:'med'}});
    }
    const left=is('rail-evidence')?104:64;
    if (is('green-navigation')) {
      rect(64,28,1152,28,'none',c.line,14);
      rect(1040,28,176,28,c.primary,'none',14);
      text(label,1060,30,144,26,15,'#FFFFFF',true);
    } else if (is('rail-evidence')) {
      rect(28,30,6,640,c.primary);
      text(label,104,28,600,28,16,c.muted,true);
    } else if (is('academic-evidence')) {
      text(label,64,30,600,28,16,c.muted,true);
    }
    const titleY=is('neutral-editorial')?46:is('dark-editorial')?52:78;
    text(body.title,left,titleY,1216-left,115,is('neutral-editorial')?46:42,is('light-editorial')?c.ink:c.primary,true);
    if (is('academic-evidence')) rule(64,179,1152);
    if (is('neutral-editorial')) rule(64,179,1152,'#222222');

    if (index===0) {
      if (is('light-editorial')) {
        rect(64,218,548,110,'#FFFFFF','none',12);
        rect(636,218,580,110,'#FFFFFF','none',12);
        text(body.accuracy,84,244,508,60,36,c.primary,true);
        text(body.latency,656,244,540,60,36,c.ink,true);
        text(body.comparison,64,345,800,34,22,c.muted);
        table(64,394,1152,220);
        text(body.limit,64,632,1152,32,23,c.muted);
      } else if (is('academic-evidence')) {
        table(64,234,760,300);
        text(body.comparison,874,231,330,42,24,c.muted);
        text(body.accuracy,874,304,330,88,32,c.primary,true);
        text(body.latency,874,421,330,90,32,c.ink,true);
        text(body.limit,64,591,1152,48,25,c.ink);
      } else if (is('dark-editorial')) {
        text(body.comparison,64,228,340,40,25,c.muted);
        text(body.accuracy,64,309,380,104,43,c.primary,true);
        text(body.latency,64,446,380,104,39,c.ink,true);
        table(472,236,744,318,'dark');
        text(body.limit,64,610,1152,45,25,c.muted);
      } else if (is('green-navigation')) {
        table(64,231,1152,264);
        rule(64,529,1152,c.line);
        text(body.comparison,64,553,270,70,24,c.muted);
        text(body.accuracy,369,550,390,80,32,c.primary,true);
        text(body.latency,810,550,406,80,32,c.primary,true);
        text(body.limit,64,637,1152,34,23,c.muted);
      } else if (is('rail-evidence')) {
        table(104,251,735,290,'flat');
        text(body.comparison,885,245,315,52,24,c.muted);
        text(body.accuracy,885,321,315,85,30,c.primary,true);
        text(body.latency,885,438,315,85,30,c.ink,true);
        // Two measured quantities are distinct roles; sand only marks latency.
        rect(885,417,54,4,'#E8CDA9');
        text(body.limit,104,612,1096,44,25,c.muted);
      } else {
        table(64,241,1152,285,'flat');
        text(body.comparison,64,554,270,68,24,c.muted);
        text(body.accuracy,373,549,389,80,32,c.ink,true);
        text(body.latency,812,549,404,80,32,c.ink,true);
        text(body.limit,64,639,1152,33,23,c.muted);
      }
    } else if (is('dark-editorial')) {
      flow(64,233,290,true);
      text(body.filter,460,323,740,49,32,c.ink,true);
      text(body.ranker,460,410,740,49,32,c.ink,true);
      text(body.claim,460,513,740,88,32,c.primary,true);
      text(body.limit,460,618,740,46,23,c.muted);
    } else if (is('academic-evidence')) {
      flow(64,246,1152);
      text(body.filter,346,386,270,52,25,c.primary,true);
      text(body.ranker,666,386,300,52,25,c.ink,true);
      rule(64,474,1152);
      text(body.claim,64,511,1152,72,29,c.ink,true);
      text(body.limit,64,610,1152,47,25,c.muted);
    } else if (is('rail-evidence')) {
      flow(104,268,1096,false,true);
      text(body.filter,381,400,272,62,25,c.primary,true);
      text(body.ranker,681,400,280,62,25,c.ink,true);
      text(body.claim,104,520,1096,88,32,c.ink,true);
      text(body.limit,104,630,1096,35,23,c.muted);
    } else if (is('neutral-editorial')) {
      flow(64,277,1152,false,true);
      text(body.filter,345,397,286,53,25,c.ink,true);
      text(body.ranker,655,397,299,53,25,c.ink,true);
      text(body.claim,64,524,1152,80,34,c.ink,true);
      text(body.limit,64,637,1152,33,23,c.muted);
    } else {
      flow(64,272,1152);
      text(body.filter,344,409,282,55,25,c.primary,true);
      text(body.ranker,657,409,300,55,25,c.ink,true);
      if (is('green-navigation')) rect(64,516,1152,86,c.pale,'none',12);
      text(body.claim,is('green-navigation')?84:64,534,is('green-navigation')?1112:1152,62,29,c.ink,true);
      text(body.limit,64,634,1152,36,23,c.muted);
    }
    const sourceColor=is('academic-evidence')?'#0077CC':c.muted;
    text(copy.source,left,685,1216-left,26,16,sourceColor);
    s.speakerNotes.textFrame.setText(`[slide-id:S0${index+1}] [role:main]\nSource: candidate-filter-fixture-v1, original synthetic teaching values.\nDisplay candidate: ${item.id}. Presentation-only cards: ${item.cards.join(' + ')}.\nIdentical required copy, table rows, mechanism nodes and claims across candidates. No real benchmark or full-theme validation claim.`);
  }
  return p;
}

if (process.argv[1] && import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href) {
  if (!process.argv[2]) throw new Error('Usage: node build_comparison.mjs /new/draft-directory');
  const out=path.resolve(process.argv[2]);
  await fs.mkdir(out); // Refuse to overwrite a prior build.
  for(const item of manifest.items) {
    const p=buildComparison(item);
    await (await PresentationFile.exportPptx(p)).save(path.join(out,`${item.id}.pptx`));
  }
  console.log('Six two-page drafts exported. Finalization and visual review are still required.');
}
