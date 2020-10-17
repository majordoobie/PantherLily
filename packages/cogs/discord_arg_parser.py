"""
discord_arg_parser is used to parse arguments for discord bot commands
"""


async def arg_parser(arg_dict, arg_string):
    """'Parses the arg_string to build a dictionary payload containing
    the flags and arguments used by the the discord command.
    Example:
        arg_dict = {
            'option1': {
                'default' : None,
                'flags': ['-o','--option1'],
                'switch': False,
                'switch_action': 'False,
                'required' : False
            }
        }
    Attributes
    ----------
    arg_dict: dict
        Dictionary containing instructions to parse the arg_string
    arg_dict.default: str or bool
        Default value to assign to an argument that was not used.
    arg_dict.flags: list
        Accepted strings to indicate what flag was used
    arg_dict.switch: bool
        Indicate if an argument follows the flag
    arg_dict.switch_action: bool
        Bool to return if switch is present
    arg_dict.required: bool
        Raise an error if the flag was required
    arg_string: str
        String to parse to build the return dictionary payload. These are space delimited
    Returns
    -------
        Dictionary containing all the registered commands and their value.
        return_dict = {
                "flag1": "[arg]",            # If switch=False
                "flag2": "[switch_action]"   # If switch=True
                "flag3": "[default]"         # If flag not used will always use ['default']
            }
    """
    # Empty return payload
    parsed_args = {}

    # Create required arguments dictionary and used directory
    required_flags = {}
    used_flags = {}

    # Set required dict
    for flag, dictionary in arg_dict.items():
        if dictionary['required']:
            required_flags[flag] = False
        used_flags[flag] = False

    # If arg_string is empty
    if (arg_string is None) and (len(required_flags.keys()) == 0):
        for flag, dictionary in arg_dict.items():
            parsed_args[flag] = dictionary['default']
        parsed_args['positional'] = None
        return parsed_args
    # If arg_string is empty but required arguments are expected
    elif arg_string is None:
        missing_flags = await get_missing_flags(required_flags, arg_dict)
        raise RuntimeError(get_req_arguments_not_used(missing_flags))


    # create parsed_args
    arg_list = arg_string.split()

    # Main parser
    for flag, dictionary in arg_dict.items():
        for arg in arg_list:
            if arg in dictionary['flags']:  # If a command argument is found
                # If flag is required, set it to "used/True"
                if flag in required_flags:
                    required_flags[flag] = True
                # Set used flag
                used_flags[flag] = True

                # Get position of flag in the command line argument
                dict_index = dictionary['flags'].index(arg)
                arg_index = arg_list.index(dictionary['flags'][dict_index])

                # Handle if the flag is a switch
                if dictionary['switch']:
                    parsed_args[flag] = dictionary['switch_action']
                    arg_list.pop(arg_index)

                # Handle if it is a normal flag + argument
                elif dictionary['switch'] is False:
                    if (arg_index + 1) < len(arg_list):
                        argument = arg_list.pop(arg_index + 1)
                        if argument in all_flags(arg_dict):
                            flag_error = arg_list[arg_index]
                            raise RuntimeError(f"\n`{flag_error}` positioned behind a registered "
                                               f"flag `{argument}`")
                        arg_list.pop(arg_index)
                        parsed_args[flag] = argument
                    else:
                        flag_error = dictionary['flags'][dict_index]
                        raise RuntimeError(f"\nArgument expected after `{flag_error}` flag")

    # Make sure not arguments were left behind
    missing_flags = await get_missing_flags(required_flags, arg_dict)
    if missing_flags:
        raise RuntimeError(get_req_arguments_not_used(missing_flags))

    # Set unused arguments to default
    for flag, used in used_flags.items():
        if used is False:
            parsed_args[flag] = arg_dict[flag]['default']

    # If any arguments remain, concat them together and return it
    if arg_list:
        parsed_args['positional'] = ' '.join(arg_list)
    else:
        parsed_args['positional'] = None
    return parsed_args


async def get_missing_flags(required_flags, arg_dict):
    """
    Function checks if arguments were not used
    Parameters
    ----------
    required_flags: dict
        Dictionary containing the flag name and bool if it was utilized in the arg_list
    arg_dict: dict
        Dictionary containing instructions to parse the arg_string
    Returns
    -------
    missing_flags: list
        List containing the flags that were not used
    """
    return [arg_dict[k]['flags'][0] for k, v in required_flags.items() if v is False]


def all_flags(arg_dict):
    """
    Provides an iterable to check against all flags
    Parameters
    ----------
    arg_dict: dict
        Dictionary containing instructions to parse the arg_string
    Returns
    -------
    _all_flags: list
        List containing all the flag combinations
    """
    _all_flags = []
    for k, v in arg_dict.items():
        for i in v['flags']:
            _all_flags.append(i)
    return _all_flags


def get_req_arguments_not_used(missing_flags):
    return ('\nRequired argument(s) were not used \n\n '
            f'-> `{missing_flags}`')
