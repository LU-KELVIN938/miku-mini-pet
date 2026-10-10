// Preview model of the installed Codex animation contract; never patches Codex.
export const rows = {
  idle: {row: 0, durations: [280,110,110,140,140,320].map(x => x*6)},
  'running-right': {row: 1, durations: [120,120,120,120,120,120,120,220]},
  'running-left': {row: 2, durations: [120,120,120,120,120,120,120,220]},
  waving: {row: 3, durations: [140,140,140,280]},
  jumping: {row: 4, durations: [140,140,140,140,280]},
  failed: {row: 5, durations: [140,140,140,140,140,140,140,240]},
  waiting: {row: 6, durations: [150,150,150,150,150,260]},
  running: {row: 7, durations: [120,120,120,120,120,220]},
  review: {row: 8, durations: [150,150,150,150,150,280]}
};

export function makeTimeline({paint, manual = false}) {
  let frames = [], index = 0, loopStart = 0, elapsed = 0, timer = null;
  let state = 'idle';
  const frame = () => frames[index];
  const cancel = () => {if (timer !== null) clearTimeout(timer); timer = null;};
  function schedule() {
    if (manual || frames.length === 1) return;
    timer = setTimeout(() => {timer = null; next(); schedule();}, frame().duration);
  }
  function next() {
    index++;
    if (index >= frames.length) index = loopStart;
    paint(frame());
  }
  function setState(nextState, {loop = false, reducedMotion = false, lookFrame = null} = {}) {
    if (!rows[nextState]) throw Error('Unknown native state: ' + nextState);
    cancel(); state = nextState; elapsed = 0; index = 0;
    const sequence = name => rows[name].durations.map((duration, column) => ({row: rows[name].row, column, duration}));
    // The actual overlay allows pointer/caret look only in these states.
    const acceptsLook = ['idle', 'running', 'waving'].includes(state);
    if (lookFrame && acceptsLook) {
      frames = [{...lookFrame, duration: Infinity}]; loopStart = 0;
    } else if (reducedMotion) {
      frames = [sequence(state)[0]]; loopStart = 0;
    } else if (state === 'idle' || loop) {
      frames = sequence(state); loopStart = 0;
    } else {
      const action = sequence(state);
      frames = [...action, ...action, ...action, ...sequence('idle')];
      loopStart = action.length * 3;
    }
    paint(frame()); schedule();
  }
  function advance(ms) {
    if (!manual || !Number.isFinite(ms) || ms < 0) throw Error('Manual clock requires nonnegative milliseconds');
    if (frames.length === 1) return frame();
    elapsed += ms;
    while (elapsed >= frame().duration) {elapsed -= frame().duration; next();}
    return frame();
  }
  return {setState, advance, getFrame: frame, stop: cancel};
}
