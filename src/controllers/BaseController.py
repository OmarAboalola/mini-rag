''' in java :

public class BaseController {

    protected Settings appSettings;

    public BaseController() {
        this.appSettings = Config.getSettings();
    }
}}
    '''
from helpers.config import get_settings
import os
class BaseController:
    
    def __init__(self):

        self.app_settings = get_settings()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.files_dir = os.path.join(
            base_dir, "assets/files"
            )