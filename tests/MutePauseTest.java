package kr.ioniq5.mutepause;
import com.daudio.app.dipo.service.DipoService;
public class MutePauseTest {
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args)throws Exception {
        KeyStroke key=new KeyStroke();
        check(!key.accept(0,5,100,100,0,0),"down waits");
        check(key.accept(1,5,100,175,0,0),"physical short release");
        check(!key.accept(1,5,100,175,0,0),"duplicate");
        key.accept(0,5,200,200,0,0);key.accept(0,5,200,280,1,0);
        check(!key.accept(1,5,200,300,0,0),"repeated press");
        key.accept(0,5,400,400,0,0);check(!key.accept(1,5,400,1250,0,0),"long hold");
        key.accept(0,5,1400,1400,0,0);check(!key.accept(1,5,1400,1500,0,32),"canceled");
        check(!key.accept(0,-1,2000,2000,0,0),"virtual");
        Player p=new Player(MutePauseTest.class.getClassLoader());
        DipoService s=new DipoService();DipoService.instance=s;
        check(p.service()==s && p.safe(s) && p.playing(s),"active music");
        p.pause(s);check(s.pauses==1&&!p.playing(s)&&p.safe(s),"pause keeps context eligible");
        p.play(s);check(s.plays==1&&p.playing(s),"dedicated immediate play");
        for(String condition:new String[]{"inactive","power","ivr","telematics","call","siri","phone","speech","mode"}) {
            s=new DipoService();
            if(condition.equals("inactive"))s.activated=false;
            if(condition.equals("power"))s.power=true;
            if(condition.equals("ivr"))s.call=true;
            if(condition.equals("telematics"))s.tmu=true;
            if(condition.equals("call"))s.owner.status=1;
            if(condition.equals("siri"))s.siri=true;
            if(condition.equals("phone"))s.owner.phone=1;
            if(condition.equals("speech"))s.owner.speech=1;
            if(condition.equals("mode"))s.mode.mode=1;
            check(!p.safe(s),condition);
        }
        System.out.println("Player/key integration PASS: immediate explicit Play, playback/context split, stock-key filters, interruption guards");
    }
}
