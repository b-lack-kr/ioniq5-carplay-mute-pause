package kr.ioniq5.mutepause;

import java.util.PriorityQueue;

/** Deterministic time and explicit state changes; no Android or live vehicle calls. */
public final class PauseGateTest {
    private static int checked;
    private static void check(boolean okay,String why) {
        checked++;
        if (!okay) throw new AssertionError(why);
    }
    private static final class Task implements Comparable<Task> {
        final long at,order; final Runnable action;
        Task(long t,long n,Runnable a){at=t;order=n;action=a;}
        public int compareTo(Task other){return at==other.at?Long.compare(order,other.order):Long.compare(at,other.at);}
    }
    private static final class Fake implements PauseGate.Port {
        final PriorityQueue<Task> queue=new PriorityQueue<Task>();
        final PauseGate gate=new PauseGate(this);
        Object service=new Object();
        boolean muted,playing=true,safe=true,pauseFails,playFails,reentrant;
        int pauses,plays,failures; long now=100,order,pauseAckDelay;
        Fake(){gate.initialize();}
        public Object service(){return service;}
        public boolean muted(Object s){return muted;}
        public boolean safe(Object s){return safe;}
        public boolean playing(Object s){return playing;}
        public void pause(Object s)throws Exception {
            pauses++;
            if(reentrant)gate.manualAction();
            if(pauseFails)throw new Exception("synthetic pause failure");
            if(pauseAckDelay==0)playing=false;
            else if(pauseAckDelay>0)after(pauseAckDelay,new Runnable(){public void run(){playing=false;}});
        }
        public void play(Object s)throws Exception {
            plays++;
            if(reentrant)gate.manualAction();
            if(playFails)throw new Exception("synthetic play failure");
            playing=true;
        }
        public void later(Runnable r,long delay){queue.add(new Task(now+delay,order++,r));}
        public void failed(Exception e){failures++;}
        void muteKey(boolean state){muted=state;now++;gate.release(now,now);}
        void volume(boolean state){muted=state;gate.refresh();}
        void after(long delay,Runnable r){later(r,delay);}
        void advance(long duration) {
            long end=now+duration;int guard=0;
            while(!queue.isEmpty()&&queue.peek().at<=end) {
                if(++guard>200)throw new AssertionError("unbounded loop");
                Task t=queue.remove();now=t.at;t.action.run();
            }
            now=end;
        }
        void drain(){int guard=0;while(!queue.isEmpty()){if(++guard>200)throw new AssertionError("unbounded queue");advance(queue.peek().at-now);}}
        void pauseOwned(){muteKey(true);drain();check(pauses==1&&!playing,"pause ownership prepared");}
    }
    private static void ordinary() {
        Fake f=new Fake();f.pauseOwned();f.muteKey(false);f.drain();
        check(f.plays==1&&f.playing,"mute-key unmute resumes");
        f.volume(false);f.volume(false);f.drain();check(f.plays==1,"resume consumed once");
        f.muteKey(true);f.drain();f.volume(false);f.drain();
        check(f.pauses==2&&f.plays==2,"next cycle and volume unmute");
        f=new Fake();f.playing=false;f.muteKey(true);f.drain();f.volume(false);f.drain();
        check(f.pauses==0&&f.plays==0,"already user paused stays paused");
        f=new Fake();f.muted=true;f.gate.initialize();f.muteKey(false);f.drain();
        check(f.pauses==0&&f.plays==0,"initial mute is not owned");
        f=new Fake();f.pauseOwned();f.playing=true;f.volume(false);f.drain();
        check(f.plays==0,"externally resumed needs no duplicate play");
    }
    private static void delayedAndStable() {
        final Fake f=new Fake();f.pauseOwned();f.gate.refresh();
        f.after(350,new Runnable(){public void run(){f.muted=false;}});f.drain();
        check(f.plays==1,"delayed MICOM volume unmute retries");
        final Fake g=new Fake();g.muteKey(true);g.after(150,new Runnable(){public void run(){g.muted=false;}});g.drain();
        check(g.pauses==0&&g.plays==0,"one mute sample is not stable");
        final Fake h=new Fake();h.pauseOwned();h.volume(false);h.after(150,new Runnable(){public void run(){h.muted=true;}});h.drain();
        check(h.plays==0,"unstable unmute does not play");
        h.volume(false);h.drain();check(h.plays==1,"later stable unmute still owns original pause");
        Fake i=new Fake();i.pauseOwned();i.volume(true);i.drain();
        check(i.plays==0&&i.queue.isEmpty(),"unchanged mute ends bounded poll");
        i.volume(false);i.drain();check(i.plays==1,"subsequent real unmute resumes");
        final Fake j=new Fake();j.gate.release(++j.now,j.now);j.after(350,new Runnable(){public void run(){j.muted=true;}});j.drain();
        check(j.pauses==1,"delayed mute also waits for stable readback");
    }
    private static void cancelled() {
        Fake f=new Fake();f.muteKey(true);f.muteKey(false);f.drain();check(f.pauses==0,"rapid toggle cancels queued pause");
        f=new Fake();f.pauseOwned();f.muteKey(false);f.gate.manualAction();f.drain();check(f.plays==0,"manual action cancels queued resume");
        f=new Fake();f.pauseOwned();f.gate.manualAction();f.volume(false);f.drain();check(f.plays==0,"manual action while muted revokes token");
        f=new Fake();f.muteKey(true);f.gate.manualAction();f.drain();check(f.pauses==0,"manual pause override while debounce pending");
        f=new Fake();f.pauseOwned();f.gate.reset();f.volume(false);f.drain();check(f.plays==0,"disconnect reset revokes token");
        f=new Fake();f.pauseOwned();f.gate.initialize();f.volume(false);f.drain();check(f.plays==0,"new session on same service revokes token");
        f=new Fake();f.pauseOwned();f.volume(false);f.service=new Object();f.drain();check(f.plays==0,"service replacement while pending");
        f=new Fake();f.muteKey(true);f.gate.initialize();f.drain();check(f.pauses==0,"session replacement while pause pending");
        f=new Fake();f.reentrant=true;f.pauseOwned();f.volume(false);f.drain();check(f.plays==1,"own synchronous media calls are not manual overrides");
    }
    private static void safetyAndFailure() {
        Fake f=new Fake();f.safe=false;f.muteKey(true);f.drain();f.volume(false);f.drain();
        check(f.pauses==0&&f.plays==0,"unsafe context never owns pause");
        f=new Fake();f.pauseOwned();f.safe=false;f.volume(false);f.drain();f.safe=true;f.gate.refresh();f.drain();
        check(f.plays==0,"call or mode change discards resume even if eligibility returns");
        f=new Fake();f.pauseOwned();f.volume(false);f.safe=false;f.drain();check(f.plays==0,"disabled or call during delayed resume");
        f=new Fake();f.pauseFails=true;f.muteKey(true);f.drain();f.pauseFails=false;f.playing=false;f.volume(false);f.drain();
        check(f.failures==1&&f.plays==0,"failed pause cannot later resume");
        f=new Fake();f.pauseOwned();f.playFails=true;f.volume(false);f.drain();f.playFails=false;f.gate.refresh();f.drain();
        check(f.failures==1&&f.plays==1,"failed play is not automatically repeated");
        f=new Fake();f.muteKey(true);f.playing=false;f.drain();f.volume(false);f.drain();
        check(f.pauses==0&&f.plays==0,"user pauses between release and confirmation");
        f=new Fake();f.pauseOwned();f.volume(false);f.playing=true;f.drain();check(f.plays==0,"external play during resume debounce");
    }
    private static void acknowledgement() {
        Fake f=new Fake();f.pauseAckDelay=600;f.muteKey(true);f.advance(240);
        check(f.pauses==1&&f.playing,"pause issued while phone acknowledgement pending");
        f.volume(false);f.advance(240);check(f.plays==0,"unmute waits pending own pause");
        f.drain();check(f.plays==1&&f.playing,"late pause acknowledgement followed by one play");
        f=new Fake();f.pauseAckDelay=-1;f.muteKey(true);f.advance(240);f.volume(false);f.drain();
        check(f.plays==0&&f.queue.isEmpty(),"no acknowledgement times out without autoplay");
        f=new Fake();f.pauseAckDelay=360;f.muteKey(true);f.advance(240);f.volume(false);f.advance(240);
        f.volume(false);f.drain();check(f.plays==1,"repeated volume retains pending pause ownership");
        f=new Fake();f.pauseAckDelay=480;f.muteKey(true);f.advance(240);f.gate.manualAction();
        f.volume(false);f.drain();check(f.plays==0,"manual action cancels pending pause acknowledgement ownership");
    }
    private static void eventAndStartup() {
        Fake f=new Fake();f.muteKey(true);long event=f.now;f.gate.release(event,event);f.drain();check(f.pauses==1,"duplicate physical event");
        f.muted=false;f.gate.release(event-1,f.now);f.drain();check(f.plays==0,"old release event ignored");
        f.gate.release(f.now+1,f.now+2000);f.drain();check(f.plays==0,"expired event ignored");
        f.gate.release(f.now+2,f.now+1);f.drain();check(f.plays==0,"future event ignored");
        f=new Fake();f.service=null;f.gate.initialize();f.drain();check(f.queue.isEmpty(),"missing service seeding is bounded");
        f=new Fake();f.service=null;f.gate.initialize();f.service=new Object();f.drain();f.muteKey(true);f.drain();
        check(f.pauses==1,"delayed service initialization seeds baseline");
    }
    public static void main(String[] args) {
        ordinary();delayedAndStable();cancelled();safetyAndFailure();acknowledgement();eventAndStartup();
        System.out.println("PauseGateTest PASS: "+checked+" assertions; owned pause/resume, volume timing, stable MICOM, lifecycle, user overrides and failures");
    }
}
