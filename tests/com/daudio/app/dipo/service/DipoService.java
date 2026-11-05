package com.daudio.app.dipo.service;

/** Test-only equivalent signatures of the target DEX. */
public class DipoService {
    public static DipoService instance=new DipoService();
    public static DipoService bC(){return instance;}
    public int pauses,plays;
    public boolean activated=true,power,call,siri,tmu;
    private boolean go=true;
    public void playback(boolean state){go=state;}
    public final Audio audio=new Audio();
    public final Mode mode=new Mode();
    public final Owner owner=new Owner();
    private boolean er(){return activated;}
    private boolean isPowerOff(){return power;}
    private Audio fK(){return audio;}
    private Mode fL(){return mode;}
    private Owner fM(){return owner;}
    private boolean cN(){return tmu;}
    private boolean fX(){return call;}
    private boolean ch(){return siri;}
    private void pause(){pauses++;go=false;}
    private void k(boolean immediate){if(!immediate)throw new AssertionError("unexpected delayed play");plays++;go=true;}
    public static class Audio { public boolean mute; public boolean getUserMuteState(){return mute;} }
    public static class Mode { public int mode=115; public int getCurrentMode(){return mode;} }
    public static class Owner {
        public int phone,speech,status; public int getCallStatus(){return status;} public int getPhoneCall(){return phone;} public int getSpeech(){return speech;}
    }
}
