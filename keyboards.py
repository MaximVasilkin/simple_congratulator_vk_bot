from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_keyboard(dict_of_buttons: dict) -> dict:
    colors = {'green': VkKeyboardColor.POSITIVE,
              'red': VkKeyboardColor.NEGATIVE,
              'blue': VkKeyboardColor.PRIMARY,
              'white': VkKeyboardColor.SECONDARY}
    keyboard = VkKeyboard(one_time=False, inline=True)
    for button, color in dict_of_buttons.items():
        if not button:
            keyboard.add_line()
        else:
            keyboard.add_button(button, color=colors[color])
    return keyboard.get_keyboard()


keyboard_get_postcard = create_keyboard({'Ещё открытку': 'blue'})
