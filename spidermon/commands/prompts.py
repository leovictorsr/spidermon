monitor_prompts = {
    "enable": "Enable the {} monitor?",
    "response": "Thanks for enabling the Scrapy Monitor Suite!",
    "project_error": "The command must run inside a Scrapy project.",
    "enabled": "Spidermon was enabled succesfully!",
    "already_enabled": "Spidermon was already configured on this project!\n"
    + "Proceed to the settings.py file to further configuration.",
    "setting_already_setup": "Already exists a configuration for monitor {}\n"
    + "Proceed to the settings.py file to further configuration.",
    "limit_least": "What is the fewest amount of {} expected?",
    "limit_most": "What is the greatest amount of {} expected?",
    "list": "Which {} do you want to track? (separated by comma)",
    "dict": "What is the greatest amount of {} expected?",
    "setting_error": "Invalid input value! Do you want to input a new value?",
}

validation_prompts = {
    "enable": "Do you want to enable Item Validation?",
    "response": "Item Validation enabled succesfully!",
    "response_no_schema": "There are no available item validation schemas!",
    "response_error": "No items added for validation.",
    "validation_schema": "Select a validation framework to use from the list below:\n{}"
    + "\nWhich validation framework do you want to use? (use the number related)",
    "invalid_validation_schema": "The informed validation type isn't valid! Select one from the list.\n"
    + "Do you want to try again?",
    "module_error": "You need to install {} to use this feature.",
    "validation_list": "These are the available item schemas in your project:\n{}"
    + "\nWhich item do you want to enable validation? (use the number related)",
    "validation_list_error": "Invalid item schema! Do you want try a new schema from the list?",
    "validation_list_confirm": "Do you want to enable any more item schemas?",
}
