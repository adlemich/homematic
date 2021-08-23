!! ----- Script Buttons Menu ------ !!

!! Display States
var state_main = 0; 
var state_details = 1;
var state_leavehouse = 2;
var state_enterhouse = 3;
var state_leavehouseok = 4;
var state_idle = 5;

!! Colors
string color_white ="0x80";
string color_red = "0x81";
string color_orange = "0x82";
string color_gelb = "0x83";
string color_green = "0x84";
string color_blue = "0x85";

!! Icons
string icon_none = "";
string icon_bulp_off = "0x80";
string icon_bulp_on = "0x81";
string icon_lock_open = "0x82";
string icon_lock_locked = "0x83";
string icon_error = "0x84";
string icon_ok = "0x85";
string icon_info = "0x86";
string icon_message = "0x87";
string icon_service = "0x88";
string icon_signal_green = "0x89";
string icon_signal_yellow = "0x8A";
string icon_signal_red = "0x8B";

!! Default Strings
string seperator = "------------";

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!! Init target values for display
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

string line1_text  = " ";
string line1_color = color_white;
string line1_icon  = icon_none;
string line2_text  = " ";
string line2_color = color_white;
string line2_icon  = icon_none;
string line3_text  = " ";
string line3_color = color_white;
string line3_icon  = icon_none;
string line4_text  = " ";
string line4_color = color_white;
string line4_icon  = icon_none;
string line5_text  = " ";
string line5_color = color_white;
string line5_icon  = icon_none;
string line6_text  = " ";
string line6_color = color_white;
string line6_icon  = icon_none;

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Building output from systen state
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!Get Info about which button was pressed
var source = dom.GetObject("$src$").Name();
var channel = source.StrValueByIndex(".",1).StrValueByIndex(":",1);

!!Get Infos about current system state
var state_alarmOn = dom.GetObject("AlarmAnlageAN");
var state_display = dom.GetObject("Flur_Anzeige_Seite");
var window_state_OG = dom.GetObject("Status_Fenster_OG");
var window_state_EG = dom.GetObject("Status_Fenster_EG");
var window_state_KG = dom.GetObject("Status_Fenster_KG");
var battery_state_OG = dom.GetObject("Status_Batterie_OG");

if (state_alarmOn.State() == true) {
	!! COMING BACK HOME
    
	dom.GetObject("AlarmAnlageAN").State(false);
	dom.GetObject("Flur_Anzeige_Seite").State(state_enterhouse);
}
else {
	!! WE ARE AT HOME
	
	if (state_display.Value() == state_idle) {
		dom.GetObject("Flur_Anzeige_Seite").State(state_main);
	}
	else {
		if (state_display.Value() == state_enterhouse) {
			dom.GetObject("Flur_Anzeige_Seite").State(state_main);
		}
		else {
			if (channel == 1) {
			!!!!!!! BUTTON DOWN PRESSED !!!!!!!
				if (state_display.Value() == state_main) {
					dom.GetObject("Flur_Anzeige_Seite").State(state_details);
				}
				else { 
					if (state_display.Value() == state_leavehouse) {
						dom.GetObject("Flur_Anzeige_Seite").State(state_main);
					}
					else {
						if (state_display.Value() == state_details) {
						}
					}
				}
			}
			else {
			!!!!!!! BUTTON UP PRESSED !!!!!!!
				if (state_display.Value() == state_main) {
					dom.GetObject("Flur_Anzeige_Seite").State(state_leavehouse);
				}
				else {
					if (state_display.Value() == state_leavehouse) {
						dom.GetObject("Flur_Anzeige_Seite").State(state_leavehouseok);
						dom.GetObject("AlarmAnlageAN").State(true);
					}
					else {
						if (state_display.Value() == state_details) {
							dom.GetObject("Flur_Anzeige_Seite").State(state_main);
						}
					}
				}
			}
		}
	}
}

state_display = dom.GetObject("Flur_Anzeige_Seite");
	
if (state_display.Value() == state_enterhouse) {
	line1_icon  = icon_lock_open;
	line3_text  = "Willkommen";
	line3_color = color_green;
	line4_text  = "Zuhause !";
	line4_color = color_green;
	line6_icon  = icon_ok;
}

if (state_display.Value() == state_main) {
	line1_text  = "Tschüss!";
	line1_color = color_blue;
	line2_text  = seperator;
	
	if (window_state_OG.Value() == false) {
		line3_text  = "OG: alles zu";
		line3_color = color_green;
	}
	else {
		line3_text  = "OG: Fens.auf";
		line3_color = color_red;
	}
		
	if (window_state_EG.Value() == false) {
		line4_text  = "EG: alles zu";
		line4_color = color_green;
	}
	else {
		line4_text  = "EG: Fens.auf";
		line4_color = color_red;
	}
	
	if (window_state_KG.Value() == false) {
		line5_text  = "KG: alles zu";
		line5_color = color_green;
	}
	else {
		line5_text  = "KG: Fens.auf";
		line5_color = color_red;
	}
	
	line6_text  = "- Details -";
	line6_color = color_blue;
}

if (state_display.Value() == state_leavehouse) {
	line1_text  = "Bestätigen";
	line1_color = color_red;
	line2_text  = seperator;
	line3_text  = "Haus wird";
	line3_color = color_orange;
	line4_text  = "verlassen!";
	line4_color = color_orange;
	line5_text  = seperator;
	line6_text  = "Abbrechen";
	line6_color = color_blue;
}

if (state_display.Value() == state_leavehouseok) {
	line1_color = color_red;
	line1_icon  = icon_lock_locked;
	line4_text  = "Alarm scharf";
	line4_color = color_red;
	line5_text  = "Bis bald!";
	line5_color = color_gelb;
}
	
if (state_display.Value() == state_details) {
	line1_icon = icon_ok;
	line3_text = "Alles gut!";
	
	if ((window_state_OG.Value() == true)  || (window_state_EG.Value() == true) || (window_state_KG.Value() == true)) {
		line1_icon = icon_error; 
		line3_text = "Fenster auf:";		
		
		var all_windows = dom.GetObject("Fenster");
		string itemID;
		foreach(itemID, all_windows.EnumUsedIDs()) {
			var item = dom.GetObject(itemID);
			if (item.State() == true) {
				string room = item.Name().StrValueByIndex("_",1);
				if (line4_text == " ") {
					line4_text = room;
				}
				else {
					if (line5_text == " ") {
						line5_text = room;
					}
					else {
						if (line6_text == " ") {
							line6_text = room;
						}
					}
				}
			}
		}
	}
	else {
		if (battery_state_OG.Value() == false) {
			line1_icon = icon_info;
			line3_text = "Batt. leer:";
		}
	}
}

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! System Routine - setting up the hex values for output channel !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

string splitter="|";
string msgBuffer = line1_text # splitter # line1_color # splitter # line1_icon # "\t";
msgBuffer = msgBuffer # line2_text # splitter # line2_color # splitter # line2_icon # "\t";
msgBuffer = msgBuffer # line3_text # splitter # line3_color # splitter # line3_icon # "\t";
msgBuffer = msgBuffer # line4_text # splitter # line4_color # splitter # line4_icon # "\t";
msgBuffer = msgBuffer # line5_text # splitter # line5_color # splitter # line5_icon # "\t";
msgBuffer = msgBuffer # line6_text # splitter # line6_color # splitter # line6_icon # "\t";

string substitutions = "A,0x41\tB,0x42\tC,0x43\tD,0x44\tE,0x45\tF,0x46\tG,0x47\tH,0x48\tI,0x49\tJ,0x4A\tK,0x4B\tL,0x4C\tM,0x4D\tN,0x4E\tO,0x4F\tP,0x50\tQ,0x51\tR,0x52\tS,0x53\tT,0x54\tU,0x55\tV,0x56\tW,0x57\tX,0x58\tY,0x59\tZ,0x5A";
substitutions = substitutions # "\ta,0x61\tb,0x62\tc,0x63\td,0x64\te,0x65\tf,0x66\tg,0x67\th,0x68\ti,0x69\tj,0x6A\tk,0x6B\tl,0x6C\tm,0x6D\tn,0x6E\to,0x6F\tp,0x70\tq,0x71\tr,0x72\ts,0x73\tt,0x74\tu,0x75\tv,0x76\tw,0x77\tx,0x78\ty,0x79\tz,0x7A";
substitutions = substitutions # "\t0,0x30\t1,0x31\t2,0x32\t3,0x33\t4,0x34\t5,0x35\t6,0x36\t7,0x37\t8,0x38\t9,0x39\t ,0x20\t!,0x21\t\",0x22\t%,0x25\t&,0x26\t=,0x27\t(,0x28\t),0x29\t*,0x2A\t+,0x2B\t,,0x2C\t-,0x2D\t.,0x2E\t/,0x2F";
substitutions = substitutions # "\tÄ,0x5B\tÖ,0x23\tÜ,0x24\tä,0x7B\tö,0x7C\tü,0x7D\tß,0x5F\t:,0x3A\t;,0x3B\t@,0x40\t>,0x3E";

string bufferLine;
string substEntry;

string command = "0x02";
integer i = 0;
string char = "";

foreach(bufferLine, msgBuffer) {
   string line = bufferLine.StrValueByIndex(splitter, 0);
   string color = bufferLine.StrValueByIndex(splitter, 1);
   string icon = bufferLine.StrValueByIndex(splitter, 2);
   if ((line <> "") || (icon <> "")) {
      command = command # ",0x12";
      if ((line.Substr(0,2) == "0x") && (line.Length() == 4)) {
         command = command # "," # line;
         i = 12;
      }
      else {
         i = 0;
      }
      while ((i < line.Length()) && (i < 12)) {
         char = line.Substr(i, 1);
         foreach(substEntry, substitutions){
            if (char == substEntry.Substr(0,1)){command = command # substEntry.Substr(1,5);}
         }
         i = i + 1;
      }
      command = command # ",0x11," # color;
      if (icon <> "") {
         command = command # ",0x13," # icon;
      }
    }
 command = command # ",0x0A";
}
command = command # ",0x03";

dom.GetObject("BidCos-RF." # dom.GetObject("$src$").Name().StrValueByIndex(".",1) # ".SUBMIT").State(command);
