from setup import installdeps

try:
    import os
    import json
    import time
    import asyncio
    import logging
    import datetime
    import pyautogui
    import threading
    from overlay import *
    from fancycon import *

    import discord
    from discord.ui import Select, View
except:
    if not installdeps():
        print(f"Failed to install dependencies! {e}")
        time.sleep(5)
        sys.exit(1)
        
    import os
    import json
    import time
    import asyncio
    import logging
    import datetime
    import pyautogui
    import threading
    from overlay import *
    from fancycon import *

    import discord
    from discord.ui import Select, View

setcolors("pastel_purple")

abbreviations = {
    '__init__' : 'Init',
    'farmer_setup': 'Setup',
    'farmer_loop' : 'Loop',
    'check_for_stuck' : 'CheckStuck',
    'advanced_anti_stuck' : 'AntiStuck',
    'select_legends' : 'Legends',
    'get_highest_priority_object' : 'Priority',
}

logger = logging.getLogger("DBLegendsFarmer")
logging.getLogger("discord").setLevel(logging.CRITICAL)

class AbbreviationFilter(logging.Filter):
    def filter(self, record):
        record.abbrevFuncName = abbreviations.get(record.funcName, record.funcName)
        return True

logger.addFilter(AbbreviationFilter())

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s * [%(abbrevFuncName)s] %(message)s",
    handlers=[
        logging.FileHandler(filename=f"{os.getcwd()}\\logs\\{datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')}.log")
    ]
)

class ConfigFuctions:
    
    def get_config(config_path: str) -> dict:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_json = f.read()
                config_dict = json.loads(config_json)
            return config_dict
        else:
            with open(config_path, "w") as f:
                config_default = ConfigFuctions.get_default_config()
                f.write(json.dumps(config_default, indent=4))
                return config_default
    
    @staticmethod
    def get_default_config():
        
        config_default = {
            "window_name" : "MEmu",
            "image_folder" : os.path.join(os.getcwd(), "images"),
            "overlay_enabled": True,
            "functions_timer" : {
                "fix_images" : 0.5,
                "overlay_refresh" : 0.5,
                "advanced_anti_stuck" : 60.0,
            },
            "intelligent_functions" : {
                "fix_images" : False,
                "auto_update" : False,
                "advanced_anti_stuck" : True,
            },
            "configure_tries" : {
                "LookFor-Window" : 50,
                "Antistuck-Tries" : 5,
                "YesButton-Continue" : 10,
                "YesButton-StartBattle" : 10,
                "YesButton-LegendsPointer" : 10,
                "FinishedPointer-TapArrow" : 10,
                "YesButton-SkipButton" : 20,
                "SkipButton-YesButton" : 10,
            },
            "configure_offsets" : {
                "legends-y" : 90,
                "legend1-x" : 300,
                "legend2-x" : 200,
                "legend3-x" : 100,
            },
            "object_priority_list" : {
                "SkipButton": 14,
                "ArrowObject" : 13,
                "CloseButton": 12,
                "TapArrow" : 11,
                "NoButton" : 10,
                "YesButton" : 9,
                "StartBattleButton" : 8,
                "DemoCheckmark" : 7,
                "OkBattleButton" : 6,
                "ReadyButton": 5,
                "StoryButton": 4,
                "MenuButton" : 3,
                "ContinueButton" : 2,
                "MissionObject" : 1,
            },
            "discord_controller" : {
                "enabled" : False,
                "trusted-id" : "Trusted-ID-Here",
                "token" : "Token-Here-Discord",
            }
        }
        
        return config_default

class AntiStuckFunctions:
    
    @staticmethod
    def check_for_stuck(old_screenshot) -> bool:
        if pyautogui.locateOnScreen(old_screenshot, confidence=0.85):
            return True
        else:
            return False
        
    @staticmethod
    def find_all_objects(tries_per_object: int, scan_dict: dict, image_dict: dict) -> dict:
        found_objects = {}
        for image in scan_dict:
            if image in image_dict:
                for tries in range(tries_per_object):
                    located_object = pyautogui.locateCenterOnScreen(image_dict[image], confidence=0.7)
                    if located_object:
                        found_objects[image] = located_object
                        logger.info(f"Found object [{image}] at {located_object}")
                        normalprint("info", "[AntiStuckFunctions]", f"Found object [{image}] at {located_object}")
                        break
        return found_objects
    
    @staticmethod
    def get_highest_priority_object(found_objects: dict, priority_list: list) -> str:
        for object_name in priority_list:
            if object_name in found_objects:
                logger.info(f"Object [{object_name}] found, clicking")
                normalprint("info", "[AntiStuckFunctions]", f"Object [{object_name}] found, clicking")
                return object_name
        return None
    
    @staticmethod
    def click_object(object_coords: tuple, skip: bool = False) -> None:
        
        if skip:
            return None
        
        x, y = object_coords
        pyautogui.click(x, y)
    
    @staticmethod
    def discord_controller(token: str, trusted_id: int, found_objects: dict):
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop) 
        bot = discord.Bot(loop=loop)
        
        EMOJI_LIST = {
            "SkipButton": "⏭️",
            "ArrowObject": "➡️",
            "CloseButton": "❌",
            "TapArrow": "👉",
            "NoButton": "🚫",
            "YesButton": "✅",
            "StartBattleButton": "🔥",
            "DemoCheckmark": "✔️",
            "OkBattleButton": "👍",
            "ReadyButton": "🔜",
            "StoryButton": "📖",
            "MenuButton": "📋",
            "ContinueButton": "▶️",
            "MissionObject": "🎯",
            "SkipStuck" : "🚀"
        }
            
        async def selection_callback(interaction, combo_box, channel):
            AntiStuckFunctions.click_object(
                object_coords=found_objects[combo_box.values[0]] if combo_box.values[0] != "SkipStuck" else (0,0), 
                skip=True if combo_box.values[0] == "SkipStuck" else False
            )
            if combo_box.values[0] == "SkipStuck":
                await channel.send(f"Stuck state skipped | Triggered by: {interaction.user.mention}")
            else:
                await channel.send(f"Object clicked: `{combo_box.values[0]}` | Triggered by: {interaction.user.mention}")
                
            await interaction.response.send_message(f"Executed Successfully!", ephemeral=True)
            await bot.close()
        
        @bot.event
        async def on_ready():
            channel = bot.get_channel(int(trusted_id))
            pyautogui.screenshot("./ss.png")
            
            view = View()
            
            options = []
            for fobject in found_objects:
                options.append(
                    discord.SelectOption(
                        label=fobject,
                        emoji=EMOJI_LIST[fobject],
                        description=f"{found_objects[fobject]}"
                    )
                )  
            options.append(
                discord.SelectOption(
                    label="SkipStuck",
                    emoji=EMOJI_LIST["SkipStuck"],
                    description="Skip the stuck state"
                )
            )
            
            combo_box = Select(
                max_values=1,
                options=options,
                placeholder="Select an option!"
            )
            combo_box.callback = lambda x: selection_callback(x, combo_box, channel)
            
            view.add_item(combo_box)
            
            await channel.send("Stuck detected, please select the object to click", view=view, file=discord.File("ss.png"))
            os.remove("./ss.png")
            logger.info("Discord controller message sent")
            normalprint("info", "[AntiStuckFunctions]", "Discord controller message sent")
        
        bot.run(token)

class IntelligentFunctions:
    
    def __init__ (self, config: dict, image_dictionary: dict, priority_list: dict) -> None:
        self.config = config
        self.enabled_modules = []
        self.stuck_data = {"state": False, "fixed": 0}
        
        #? [Module Variables]
        self.fixer_enabled = False
        
        for module in config["intelligent_functions"]:
            if config["intelligent_functions"][module]:
                self.enabled_modules.append(module)
        logger.info(f"Enabled modules: {self.enabled_modules}")
        normalprint("info", "[IntelligentFunctions]", f"Enabled modules: {self.enabled_modules}")
        
        self.IMAGE_DICTIONARY = image_dictionary
        self.PRIORITY_LIST = priority_list
        
        if "fix_errors" in self.enabled_modules:
            self.fix_errors(action="init")
        if "auto_update" in self.enabled_modules:
            self.auto_update()
        if "advanced_anti_stuck" in self.enabled_modules:
            stuck_thread = threading.Thread(target=self.advanced_anti_stuck)
            stuck_thread.start()
    
    def fix_errors(self, action: str):
        #? [Init]
        if action == "init":
            self.fixer_enabled = True
            logger.info("Fixer enabled")
            normalprint("info", "[IntelligentFunctions]", "Fixer enabled")
        #? [Fix-Images]
        elif action == "fix-images" and self.fixer_enabled:
            raise NotImplementedError("Will implement later lmao")
    
    def auto_update(self):
        raise NotImplementedError("Will implement later lmao")
    
    def advanced_anti_stuck(self):
        
        token = self.config["discord_controller"]["token"]
        trusted_id = self.config["discord_controller"]["trusted-id"]
        
        time.sleep(1.5)
        
        while True:
            old_screenshot = pyautogui.screenshot()
            time.sleep(self.config["functions_timer"]["advanced_anti_stuck"])
            logger.info("Checking for stuck state")
            normalprint("info", "[IntelligentFunctions]", "Checking for stuck state")
            
            if AntiStuckFunctions.check_for_stuck(old_screenshot):
                logger.info("Stuck state detected")
                normalprint("info", "[IntelligentFunctions]", "Stuck state detected")
                self.stuck_data["state"] = True
                
                logger.info("Looking for objects to click")
                normalprint("info", "[IntelligentFunctions]", "Looking for objects to click")
                found_objects = AntiStuckFunctions.find_all_objects(tries_per_object=self.config["configure_tries"]["Antistuck-Tries"], scan_dict=self.PRIORITY_LIST, image_dict=self.IMAGE_DICTIONARY)
                
                if len(found_objects) < 1:
                    logger.error("No objects found")
                    normalprint("error", "[IntelligentFunctions]", "No objects found")
                    self.stuck_data["state"] = False
                    continue
                else:
                    logger.info(f"Found {len(found_objects)} total objects")
                    normalprint("info", "[IntelligentFunctions]", f"Found {len(found_objects)} total objects")
                
                if self.config["discord_controller"]["enabled"]:
                    AntiStuckFunctions.discord_controller(token, trusted_id, found_objects)
                    self.stuck_data["fixed"] += 1
                else:
                    max_object = AntiStuckFunctions.get_highest_priority_object(found_objects, self.PRIORITY_LIST)
                    
                    logger.info(f"Trying to click object [{max_object}]")
                    normalprint("info", "[IntelligentFunctions]", f"Trying to click object [{max_object}]")
                    AntiStuckFunctions.click_object(found_objects[max_object])
                    
                    self.stuck_data["fixed"] += 1
            else:
                logger.info("No stuck state detected")
                normalprint("info", "[IntelligentFunctions]", "No stuck state detected")
                
            self.stuck_data["state"] = False
                
class FarmerFunctions:
    
    def __init__ (self, config: dict) -> None:
        self.config = config
        self.image_folder = config["image_folder"] + "\\" 
        logger.info(f"Trying to find window with name [{config['window_name']}]")
        normalprint("info", "[FarmerFunctions]", f"Trying to find window with name [{config['window_name']}]")
        try:
            self.window = self.get_window(config["window_name"], self.config["configure_tries"]["LookFor-Window"])
        except:
            logger.error(f"Window with name [{config['window_name']}] not found")
            normalprint("error", "[FarmerFunctions]", f"Window with name [{config['window_name']}] not found")
            time.sleep(2)
            raise SystemExit
        logger.info(f"Window found with name [{self.window.title}]")
        normalprint("info", "[FarmerFunctions]", f"Window found with name [{self.window.title}]")
        
        self.IMAGE_DICTIONARY = {
            "ArrowObject" : self.image_folder+"arrow.png",
            "CloseButton": self.image_folder+"close.png",
            "ContinueButton" : self.image_folder+"continue.png",
            "DemoCheckmark" : self.image_folder+"demo.png",
            "LegendsPointer" : self.image_folder+"legendspointer.png",
            "FinishedPointer" : self.image_folder+"finishedpointer.png",
            "MenuButton" : self.image_folder+"menu.png",
            "MissionObject" : self.image_folder+"mission.png",
            "NoButton" : self.image_folder+"no.png",
            "OkBattleButton" : self.image_folder+"okbattle.png",
            "ReadyButton": self.image_folder+"ready.png",
            "SkipButton": self.image_folder+"skip.png",
            "StartBattleButton" : self.image_folder+"startbattle.png",
            "StoryButton": self.image_folder+"story.png",
            "TapArrow" : self.image_folder+"tap.png",
            "YesButton" : self.image_folder+"yes.png",
        }
        
        self.intelligent_functions = IntelligentFunctions(config=self.config, image_dictionary=self.IMAGE_DICTIONARY, priority_list=self.config["object_priority_list"])
        
        #? Overlay Data [dicts]
        self.loop_data = {"current": 0, "completed": 0}
        self.log_file = f"{os.getcwd()}\\logs\\{datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')}.log"
        
        if self.config["overlay_enabled"]:
            self.overlay_thread = threading.Thread(target=lambda: Overlay({"loop": "Waiting for setup to finish...", "stuck": " ", "log_file": self.log_file}, 5000, self.get_overlay_data).run())
            self.overlay_thread.start()
              
        image_folder_contents = os.listdir(self.image_folder)
        
        status = "passed"
        
        #? Image testing
        for image in self.IMAGE_DICTIONARY:
            if not os.path.exists(self.IMAGE_DICTIONARY[image]):
                logger.debug(f"Image [{image}] not found in folder")
                normalprint("warning", "[FarmerFunctions]", f"Image [{image}] not found in folder")
                if self.config["intelligent_functions"]["auto_fix_errors"] and self.config["intelligent_functions"]["enabled"]:
                    self.intelligent_functions.fix_errors(action="fix-images")
                    logger.info(f"Image [{image}] not found in folder, fixed")
                    normalprint("info", "[FarmerFunctions]", f"Image [{image}] not found in folder, fixed")
                else:
                    status = "failed"
                    logger.error(f"Image [{image}] not found in folder, auto_fix_errors is disabled")
                    normalprint("error", "[FarmerFunctions]", f"Image [{image}] not found in folder, fix_errors is disabled")
            else:
                logger.debug(f"Image [{image}] found in folder")
                normalprint("info", "[FarmerFunctions]", f"Image [{image}] found in folder")
        
        logger.info(f"Finished image check, [{status}]")
        normalprint("info", "[FarmerFunctions]", f"Finished image check, [{status}]")
        
        #? Window setup
        self.window.activate()
        self.window.maximize()
        
    def farmer_setup(self) -> None:
        logger.info("Emulator window on focus, waiting for [MenuButton] to appear")
        normalprint("info", "[farmer_setup]", "Emulator window on focus, waiting for [MenuButton] to appear")
        
        #? [MenuButton]
        self.locate_without_tries(self.IMAGE_DICTIONARY["MenuButton"], confidence=0.6, delay=0.3)
        logger.info("Game is ready to be played, starting game setup, waiting for [StoryButton] to appear")
        normalprint("info", "[farmer_setup]", "Game is ready to be played, starting game setup, waiting for [StoryButton] to appear")
        
        #? [StoryButton]
        self.locate_without_tries(self.IMAGE_DICTIONARY["StoryButton"], confidence=0.7, delay=0.3)
        logger.info("Story mode selected, waiting for [ContinueButton] to appear")
        normalprint("info", "[farmer_setup]", "Story mode selected, waiting for [ContinueButton] to appear")
        
        #? [ContinueButton]
        self.locate_without_tries(self.IMAGE_DICTIONARY["ContinueButton"], confidence=0.7, delay=0.3)
        logger.info("Continue button clicked, waiting for [YesButton] to appear")
        normalprint("info", "[farmer_setup]", "Continue button clicked, waiting for [YesButton] to appear")
        
        #? [YesButton]
        if self.locate_with_tries(self.IMAGE_DICTIONARY["YesButton"], confidence=0.7, delay=0.5, amount_tries=self.config["configure_tries"]["YesButton-Continue"]):
            logger.info("Successfully found and clicked [YesButton]")
            normalprint("info", "[farmer_setup]", "Successfully found and clicked [YesButton]")
        else:
            logger.error("Failed to find and click [YesButton]")
            normalprint("error", "[farmer_setup]", "Failed to find and click [YesButton]")
        logger.info("Waiting for [DemoCheckmark] to appear")
        normalprint("info", "[farmer_setup]", "Waiting for [DemoCheckmark] to appear")
        
        #? [DemoCheckmark]
        self.locate_without_tries(self.IMAGE_DICTIONARY["DemoCheckmark"], confidence=0.7, delay=0.3)
        logger.info("Demo checkmark clicked, waiting for [StartBattleButton] to appear")
        normalprint("info", "[farmer_setup]", "Demo checkmark clicked, waiting for [StartBattleButton] to appear")
        
        #? [StartBattleButton]
        self.locate_without_tries(self.IMAGE_DICTIONARY["StartBattleButton"], confidence=0.7, delay=0.3)
        logger.info("Start battle button clicked, waiting for [YesButton] to appear")
        normalprint("info", "[farmer_setup]", "Start battle button clicked, waiting for [YesButton] to appear")
        
        #? [YesButton]
        if self.locate_with_tries(self.IMAGE_DICTIONARY["YesButton"], confidence=0.7, delay=0.5, amount_tries=int(self.config["configure_tries"]["YesButton-StartBattle"])):
            logger.info("Successfully found and clicked [YesButton]")
            normalprint("info", "[farmer_setup]", "Successfully found and clicked [YesButton]")
        else:
            logger.error("Failed to find and click [YesButton]")
            normalprint("error", "[farmer_setup]", "Failed to find and click [YesButton]")
        logger.info("Waiting for [LegendsPointer] to appear")
        normalprint("info", "[farmer_setup]", "Waiting for [LegendsPointer] to appear")
        
        #? [LegendsPointer]
        self.select_legends(self.IMAGE_DICTIONARY["LegendsPointer"], confidence=0.7, delay=0.2, offsets=self.config["configure_offsets"])
        logger.info("Legends selected, waiting for [ReadyButton] to appear")
        normalprint("info", "[farmer_setup]", "Legends selected, waiting for [ReadyButton] to appear")
        
        #? [ReadyButton]
        self.locate_without_tries(self.IMAGE_DICTIONARY["ReadyButton"], confidence=0.7, delay=0.3)
        logger.info("Ready button clicked, waiting for [YesButton] to appear")
        normalprint("info", "[farmer_setup]", "Ready button clicked, waiting for [YesButton] to appear")
        
        #? [YesButton]
        if self.locate_with_tries(self.IMAGE_DICTIONARY["YesButton"], confidence=0.7, delay=0.5, amount_tries=int(self.config["configure_tries"]["YesButton-LegendsPointer"])):
            logger.info("Successfully found and clicked [YesButton]")
            normalprint("info", "[farmer_setup]", "Successfully found and clicked [YesButton]")
        else:
            logger.error("Failed to find and click [YesButton]")
            normalprint("error", "[farmer_setup]", "Failed to find and click [YesButton]")
            
        logger.info("Setup completed, game is ready to be farmed")
        normalprint("info", "[farmer_setup]", "Setup completed, game is ready to be farmed")
        
        self.loop_data['current'] += 1
            
    def farmer_loop(self) -> None:
        while True:
            logger.info("Waiting for match to finish")
            normalprint("info", "[farmer_loop]", "Waiting for match to finish")
            
            #? [FinishedPointer]
            self.wait_for(self.IMAGE_DICTIONARY["FinishedPointer"], confidence=0.8, delay=1.0)
            logger.info("Match finished, waiting for [TapArrow] to appear")
            normalprint("info", "[farmer_loop]", "Match finished, waiting for [TapArrow] to appear")
            
            #? [TapArrow]
            if self.locate_with_tries(self.IMAGE_DICTIONARY["TapArrow"], confidence=0.6, delay=0.7, amount_tries=int(self.config["configure_tries"]["FinishedPointer-TapArrow"])):
                logger.info("Successfully found and clicked [TapArrow]")
                normalprint("info", "[farmer_setup]", "Successfully found and clicked [TapArrow]")
            else:
                logger.error("Failed to find and click [TapArrow]")
                normalprint("error", "[farmer_setup]", "Failed to find and click [TapArrow]")
            logger.info("Waiting for [OkBattleButton] to appear")
            normalprint("info", "[farmer_loop]", "Waiting for [OkBattleButton] to appear")
            
            #? [OkBattleButton]
            self.locate_without_tries(self.IMAGE_DICTIONARY["OkBattleButton"], confidence=0.9, delay=0.3)
            logger.info("Ok battle button clicked, waiting for [TapArrow] to appear")
            normalprint("info", "[farmer_loop]", "Ok battle button clicked, waiting for [TapArrow] to appear")
            
            #? [TapArrow]
            if self.locate_with_tries(self.IMAGE_DICTIONARY["TapArrow"], confidence=0.6, delay=0.7, amount_tries=int(self.config["configure_tries"]["FinishedPointer-TapArrow"])):
                logger.info("Successfully found and clicked [TapArrow]")
                normalprint("info", "[farmer_setup]", "Successfully found and clicked [TapArrow]")
            else:
                logger.error("Failed to find and click [TapArrow]")
                normalprint("error", "[farmer_setup]", "Failed to find and click [TapArrow]")
            logger.info("Waiting for [OkBattleButton] to appear")
            normalprint("info", "[farmer_loop]", "Waiting for [OkBattleButton] to appear")
            
            #? [OkBattleButton]
            self.locate_without_tries(self.IMAGE_DICTIONARY["OkBattleButton"], confidence=0.9, delay=0.3)
            logger.info("Ok battle button clicked, waiting for [TapArrow] to appear")
            normalprint("info", "[farmer_loop]", "Ok battle button clicked, waiting for [TapArrow] to appear")
            
            #? [YesButton]
            self.locate_without_tries(self.IMAGE_DICTIONARY["YesButton"], confidence=0.7, delay=0.3)
            logger.info("Yes button clicked, waiting for [SkipButton] to appear")
            normalprint("info", "[farmer_loop]", "Yes battle button clicked, waiting for [SkipButton] to appear")
            
            #? [SkipButton]
            if self.locate_with_tries(self.IMAGE_DICTIONARY["SkipButton"], confidence=0.7, delay=0.5, amount_tries=int(self.config["configure_tries"]["YesButton-SkipButton"])
                                    , override_x = 1100):
                logger.info("Successfully found and clicked [SkipButton]")
                normalprint("info", "[farmer_setup]", "Successfully found and clicked [SkipButton]")
            else:
                logger.error("Failed to find and click [SkipButton]")
                normalprint("error", "[farmer_setup]", "Failed to find and click [SkipButton]")
            logger.info("Waiting for [YesButton] to appear")
            normalprint("info", "[farmer_loop]", "Waiting for [YesButton] to appear")
            
            #? [YesButton]
            if self.locate_with_tries(self.IMAGE_DICTIONARY["YesButton"], confidence=0.7, delay=0.5, amount_tries=int(self.config["configure_tries"]["SkipButton-YesButton"])):
                logger.info("Successfully found and clicked [YesButton]")
                normalprint("info", "[farmer_setup]", "Successfully found and clicked [YesButton]")
            else:
                logger.error("Failed to find and click [YesButton]")
                normalprint("error", "[farmer_setup]", "Failed to find and click [YesButton]")
            logger.info("Waiting for [DemoCheckmark] to appear")
            normalprint("info", "[farmer_loop]", "Waiting for [DemoCheckmark] to appear")
            
            #? [DemoCheckmark]
            self.locate_without_tries(self.IMAGE_DICTIONARY["DemoCheckmark"], confidence=0.7, delay=0.5)
            logger.info("Demo checkmark clicked, waiting for [StartBattleButton] to appear")
            normalprint("info", "[farmer_setup]", "Demo checkmark clicked, waiting for [StartBattleButton] to appear")
            
            #? [StartBattleButton]
            self.locate_without_tries(self.IMAGE_DICTIONARY["StartBattleButton"], confidence=0.7, delay=0.3)
            logger.info("Start battle button clicked, waiting for [YesButton] to appear")
            normalprint("info", "[farmer_setup]", "Start battle button clicked, waiting for [YesButton] to appear")
            
            #? [YesButton]
            if self.locate_with_tries(self.IMAGE_DICTIONARY["YesButton"], confidence=0.7, delay=0.5, amount_tries=int(self.config["configure_tries"]["YesButton-StartBattle"])):
                logger.info("Successfully found and clicked [YesButton]")
                normalprint("info", "[farmer_setup]", "Successfully found and clicked [YesButton]")
            else:
                logger.error("Failed to find and click [YesButton]")
                normalprint("error", "[farmer_setup]", "Failed to find and click [YesButton]")
            logger.info("Waiting for [LegendsPointer] to appear")
            normalprint("info", "[farmer_setup]", "Waiting for [LegendsPointer] to appear")
            
            #? [LegendsPointer]
            self.select_legends(self.IMAGE_DICTIONARY["LegendsPointer"], confidence=0.7, delay=0.2, offsets=self.config["configure_offsets"])
            logger.info("Legends selected, waiting for [ReadyButton] to appear")
            normalprint("info", "[farmer_setup]", "Legends selected, waiting for [ReadyButton] to appear")
            
            #? [ReadyButton]
            self.locate_without_tries(self.IMAGE_DICTIONARY["ReadyButton"], confidence=0.7, delay=0.3)
            logger.info("Ready button clicked, waiting for [YesButton] to appear")
            normalprint("info", "[farmer_setup]", "Ready button clicked, waiting for [YesButton] to appear")
            
            #? [YesButton]
            if self.locate_with_tries(self.IMAGE_DICTIONARY["YesButton"], confidence=0.7, delay=0.5, amount_tries=int(self.config["configure_tries"]["YesButton-LegendsPointer"])):
                logger.info("Successfully found and clicked [YesButton]")
                normalprint("info", "[farmer_setup]", "Successfully found and clicked [YesButton]")
            else:
                logger.error("Failed to find and click [YesButton]")
                normalprint("error", "[farmer_setup]", "Failed to find and click [YesButton]")
                    
                self.loop_data["current"] += 1
                self.loop_data["completed"] += 1
    
    def get_overlay_data(self) -> tuple:
        
        data = {
            "loop" : f"Current Loop: {self.loop_data['current']} | Completed Loops: {self.loop_data['completed']}",
            "stuck" : f"Stuck State: {self.intelligent_functions.stuck_data['state']} | Stucks Fixed: {self.intelligent_functions.stuck_data['fixed']}"
        }
        
        overlay_refresh = round(self.config["functions_timer"]["overlay_refresh"] * 100)
        
        return overlay_refresh, data
    
    @staticmethod
    def get_window(window_name: str, tries: int) -> pyautogui.Window:
        try_counter = 0
        window = False
        for tries in range(tries):
            try:
                window = pyautogui.getWindowsWithTitle(window_name)[0]
                break
            except:
                time.sleep(0.1)
        
        if window:
            return window
        else:
            raise Exception("Window not found")
    
    @staticmethod
    def wait_for(element_to_locate: str, confidence: float, delay: float) -> None:
        while True:
            located_object = pyautogui.locateCenterOnScreen(element_to_locate, confidence=confidence)
            if located_object:
                break
            else:
                time.sleep(delay)
        
    @staticmethod         
    def locate_without_tries(element_to_locate: str, confidence: float, delay: float) -> None:
        time.sleep(delay)
        while True:
            located_object = pyautogui.locateCenterOnScreen(element_to_locate, confidence=confidence)
            if located_object:
                x, y = located_object
                pyautogui.click(x, y)
                break
            else:
                time.sleep(delay)
    
    @staticmethod
    def locate_with_tries(element_to_locate: str, confidence: float, delay: float, amount_tries: int, override_x: int = None) -> bool:
        time.sleep(delay)
        for tries in range(amount_tries):
            located_object = pyautogui.locateCenterOnScreen(element_to_locate, confidence=confidence)
            if located_object:
                x, y = located_object
                if override_x:
                    x = override_x
                pyautogui.click(x, y)
                return True
            else:
                time.sleep(delay)
            
        return False
    
    @staticmethod
    def select_legends(pointer_element: str, confidence: float, delay: float, offsets : dict) -> None:
        time.sleep(delay)
        while True:
            located_object = pyautogui.locateCenterOnScreen(pointer_element, confidence=confidence)
            if located_object:
                x, y = located_object
                logger.info("Legends pointer found, calculating positions and clicking")
                legendsy = y + offsets["legends-y"]
                legend1x = x - offsets["legend1-x"]
                legend2x = x - offsets["legend2-x"]
                legend3x = x - offsets["legend3-x"]
                time.sleep(delay)
                pyautogui.click(legend1x, legendsy)
                logger.info(f"Clicked legend 1. | x:{legend1x}, y:{legendsy}")
                time.sleep(delay)
                pyautogui.click(legend2x, legendsy)
                logger.info(f"Clicked legend 2. | x:{legend2x}, y:{legendsy}")
                time.sleep(delay)
                pyautogui.click(legend3x, legendsy)
                logger.info(f"Clicked legend 3. | x:{legend3x}, y:{legendsy}")
                break
            else:
                time.sleep(delay)

class Cosmetic:
    
    def title():
        System.Title('DBFarmer ⏐ Made by: Takkeshi ⏐ Version: 1.0 ⏐ https://github.com/LUXTACO')
        
        window = FarmerFunctions.get_window("DBFarmer ⏐ Made by: Takkeshi ⏐ Version: 1.0 ⏐ https://github.com/LUXTACO", 10)
        window.maximize()
        
        image = """
                  ..       . 
                  77.    .^~^.
                  .J55J7^::~!JJ~ 
                   :?JPGGBPJ!:?B5:                   .~~::
                    ^~!JJJJ5GY~?GP:                  ~J~:7P?:
               .::^^~?:^!!~~7557?G!                 ^?!^.^!?!::..
         .:^~7JY55555Y?!^^.:.~?7~7:                :7!:^!77~^^^^^:. 
         .::^^~~~~~~!~^!?YJ7~~!~:~77!.     ..     .^~:^~JP#BY7~^^^^:.
                 .^^:755Y?!?PPJ7~^77YY7!!~~:.     :~.::!5B@@@&BY7^^^~:.
                .~!~~^..:.J#GYJ?^7JJ!?!~!!^:.    .~:..   .^?P&@@&P?~^~~:
             .^~!~^:. .?7~#GY?~. ~57J~:~!^.      ^^..        .7P&@&GJ~!?~
            :::....^~~^?:~G~. .:.:^!!^!~^:      :^..            :?B@&P7~J7
                    :^^^::!!:.:~?J?^:^^        .~...              .?#@#Y7J7
                       ..^:..^55BB7.          .^:..                 .Y@&P?Y!
                         ::.:~PBY~:^..        ^^..                    ~#@PJ5^
                      .^::::.~!^:::...:...   :^..                      :G@GYJ
                 .^:^^^~.::~:~~^~::.....::.^:^:..                       .P@B5^
            .:~~777~^~!~:5PPY7?5Y!^::.:...~~^^..77:.                      P@B7
            :77^!~^~:~~7:!5G#&BY7~^::^:.^~:^7JJ!~^:^.                     .B&?
           .~:~.:~:~.^:~~:^!7!!!^^::^..~!.:7YYPB!.~                        7@J
          .J:.:..:.^:.:..:.:~!~^::^:.~7!.:7J5PG#~:Y?                       .#?
          :7.:......:....:~~~^..::.^77~....~?PGB^.7Y                        P~ 
          ^~:7?........:^^^:.....:!~^^^:::..:!Y?^.^?^  .                    !. 
         .7~J5?^.....::::......:~~^!7!^:::.....:YJ^!Y:.^~??!:
         :^!Y7^:.............:^^~7J7^..::.. :^:~?555P555J!:
         .^~7^::::::::.. . .::^!7!::~:::.::~7Y5PP5YYJ7:. .
         :^:^::..::^~!7???????7!^:^~!7?JY5PGP5J?~::^~!..::
         ::.......::::::^~!7?JJJJJY55YJ?7!^:.:^:....::..:
           . ...........       .....           .........
        """
        
        text = """
         ▄▀▀█▄▄   ▄▀▀█▄▄   ▄▀▀▀█▄    ▄▀▀█▄   ▄▀▀▄▀▀▀▄  ▄▀▀▄ ▄▀▄  ▄▀▀█▄▄▄▄  ▄▀▀▄▀▀▀▄ 
        █ ▄▀   █ ▐ ▄▀   █ █  ▄▀  ▀▄ ▐ ▄▀ ▀▄ █   █   █ █  █ ▀  █ ▐  ▄▀   ▐ █   █   █ 
        ▐ █    █   █▄▄▄▀  ▐ █▄▄▄▄     █▄▄▄█ ▐  █▀▀█▀  ▐  █    █   █▄▄▄▄▄  ▐  █▀▀█▀  
          █    █   █   █   █    ▐    ▄▀   █  ▄▀    █    █    █    █    ▌   ▄▀    █  
         ▄▀▄▄▄▄▀  ▄▀▄▄▄▀   █        █   ▄▀  █     █   ▄▀   ▄▀    ▄▀▄▄▄▄   █     █   
        █     ▐  █    ▐   █         ▐   ▐   ▐     ▐   █    █     █    ▐   ▐     ▐   
        ▐        ▐        ▐                           ▐    ▐     ▐                  
        """
        
        banner = Add.Add(text, image, 4, True)
        banner = Colorate.Diagonal(Colors.DynamicMIX((VALID_COLOR_PRESETS["white"], VALID_COLOR_PRESETS["pastel_purple"])), banner)
        print(banner)
  
if __name__ == "__main__":
    System.Clear()
    Cosmetic.title()
    pyautogui.useImageNotFoundException(False)
    farmer = FarmerFunctions(config=ConfigFuctions.get_config("config.json"))
    farmer.farmer_setup()
    farmer.farmer_loop()
