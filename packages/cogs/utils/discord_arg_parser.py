import shlex


class DiscoArgParseException(Exception):
    def __init__(self, msg):
        self.msg = msg
        self.base_name = 'Discord Argument Parser Error'
        super().__init__(msg)


class MissingRequiredException(DiscoArgParseException):
    def __init__(self, missing_args: list):
        self.missing_args = missing_args
        self.base_name = 'Missing Required Flags'
        self.msg = ('Required argument(s) were not used:\n\n'
                    f'-> `{missing_args}`')
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class DiscordCommandError(DiscoArgParseException):
    def __init__(self, msg: str):
        self.msg = msg
        self.base_name = 'Argument Error'
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class DiscordArgParse:
    """
    DiscoArgParse makes it easy to write command-line interfaces by parsing the
    string by methods below:
        -> async def bot_command(self, ctx, *, args=None):

    A dictionary (arg_dict) must be provided along with the string from the bot (arg_string)

    Example:
        arg_string = '<command_prefix> <command> --option1 <value>
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

    arg_string: str
        String from async def bot_command(self, ctx, *, args=None)

    arg_dict.flags: list [required]
        List of strings used to indicate a specific flag is chosen. By convention these
        are prefixed with - or -- for example -e --example

    arg_type: str [optional][default=str]
        Set a data type for the parameter. By default it will be a string

    arg_dict.switch: bool [optional][default=False]
        When set to True, the flag will act as a boolean with the value of "switch_action".

        Example:
            "verbose" : {"flags": ["--verbose"], "switch": True}

             -> Command: <bot_prefix> <command> --verbose

    arg_dict.switch_action: bool [optional][default=True]
        Value a flag contains when "switch" is set to True

    arg_dict.default: bool [optional][default=None]
        Default value of a flag when the flag was not used by the user. This value is
        only evaluated when "switch" is False

    arg_dict.required: bool
        Raise an error to the user when the flag was not specified in the arg_string

    Raises
    ------
    MissingRequiredException:
        Exception is raised when the arg_string is missing required flags

    DiscordCommandError:
        Exception is raised when a potential arg_string error is found such as using
        multiple flags after another for example:

            -> Command: <bot_prefix> <command> <flag> <flag> <flag>


    Notes
    -----
    At a bare minimum you need to provide the flags list
        "flag1" : {"flags": ["--flag1"]}

    This configuration will provide the following:
        "flag1": {
                    "flags": ["--flag1"],
                    "switch": False,
                    "switch_action": True,
                    "required": False
                    "default": None
                }
    """

    def __init__(self, arg_dict: dict, arg_string: str):
        # Parameters
        self.arg_dict = _clean_dict(arg_dict)
        self.arg_string = arg_string
        if arg_string:
            self.arg_list = shlex.split(arg_string)

        self.used_flags = {}
        self.parsed_args = {}  # Final product

        self._get_required()
        self._set_all_flags()

        if not self.arg_string:
            self._empty_string_parse()
        else:
            self._arg_parse()

        for key, value in self.parsed_args.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        return self.parsed_args[key]

    def __contains__(self, key):
        return key in self.parsed_args

    def __repr__(self):
        return repr(self.parsed_args)

    def _get_required(self):
        """
        Iterates over the arg_dict to see if any of the flags specified by the dictionary are
        meant to be required. If they are, add them to the required_flags dictionary with the
        value of False. The False value is later used to determine if the flag is present in
        the arg_string.

        Attributes
        ----------
        required_flags: dict
            The dictionary keys are used as a list of flags that are deem to be required.
            The values are used as an indicator if the flag was present in the arg_string.

        """
        self.required_flags = {}
        for flag, _dict in self.arg_dict.items():
            if _dict['required']:
                self.required_flags[flag] = False
            self.used_flags[flag] = False

    def _set_all_flags(self):
        """
        Creates a list of all the flags for quicker iteration later on
        """
        all_flags = []
        for key, value in self.arg_dict.items():
            for flag in value['flags']:
                all_flags.append(flag)
        self.all_flags = all_flags

    def _empty_string_parse(self):
        """
        This parser is only called when arg_string is None. The parser will then check to see
        if there are any required arguments that were supposed to be present or if there are
        default values to be set when not arguments are present.
        """
        if len(self.required_flags.keys()) == 0:
            for flag, _dict in self.arg_dict.items():
                self.parsed_args[flag] = _dict['default']
            self.parsed_args['positional'] = None
        else:
            missing_flags = self._get_missing_flags()
            raise MissingRequiredException(missing_flags)

    def _arg_parse(self):
        for flag, _dict in self.arg_dict.items():
            for arg in self.arg_list:
                # If the item in the list is an argument...
                if arg in _dict['flags']:
                    # Set flags as used in the required and used dicts
                    if flag in self.required_flags.keys():
                        self.required_flags[flag] = True
                    self.used_flags[flag] = True

                    # Get position of the flag in the arg_list
                    dict_flag = _dict['flags'].index(arg)
                    arg_index = self.arg_list.index(_dict['flags'][dict_flag])

                    ## Handle if the flag is just a bool switch
                    if _dict['switch']:
                        self.parsed_args[flag] = _dict['switch_action']
                        self.arg_list.pop(arg_index)

                    ## Handle if the flag has a follow up value
                    elif _dict['switch'] is False:
                        ### If flag is not a switch, there should be a arg after the flag
                        if (arg_index + 1) < len(self.arg_list):
                            argument = self.arg_list.pop(arg_index + 1)
                            ### If argument is found in the flag list - throw error
                            if argument in self.all_flags:
                                msg = f'`{argument}` positioned behind a registered flag `{argument}`'
                                raise DiscordCommandError(msg)

                            if _dict['type'] == 'int':
                                try:
                                    argument = int(argument)
                                except ValueError:
                                    msg = f'Expected to be an integer, got a string instead'
                                    raise DiscordCommandError(msg)

                            self.arg_list.pop(arg_index)
                            self.parsed_args[flag] = argument

                        else:
                            argument_error = _dict['flags'][dict_flag]
                            msg = f'Argument expected after `{argument_error}` flag'
                            raise DiscordCommandError(msg)

        # Determine if required flags were not used
        missing = self._get_missing_flags()
        if missing:
            raise MissingRequiredException(missing)

        # set unused flags to default
        for flag, used in self.used_flags.items():
            if used is False:
                if self.arg_dict[flag]['switch']:
                    if self.arg_dict[flag]['switch_action']:
                        self.parsed_args[flag] = False
                    else:
                        self.parsed_args[flag] = True
                else:
                    self.parsed_args[flag] = self.arg_dict[flag]['default']

        # Concat remaining args
        if self.arg_list:
            self.parsed_args['positional'] = ' '.join(self.arg_list)
        else:
            self.parsed_args['positional'] = None

    def _get_missing_flags(self) -> list:
        """
        Iterates over the required_flags dictionary to determine if there are any values
        that is still set to False. If so, add them to a list and return them.

        Returns
        -------
        missing: list
            List full of flags that have not been used
        """
        missing = []
        for key, value in self.required_flags.items():
            if value is False:
                missing.append(self.arg_dict[key]['flags'][0])
        return missing


def _clean_dict(arg_dict: dict) -> dict:
    """
    Function adds the rest of the dictionary values as the "Defaults"

    Parameters
    ----------
    arg_dict: dict
        Dictionary with the user defined arg values

    Returns
    -------
    arg_dict: dict
        Returns the same modified dictionary
    """
    for key, _dict in arg_dict.items():
        if 'default' not in _dict.keys():
            _dict['default'] = None

        if 'required' not in _dict.keys():
            _dict['required'] = False

        if 'switch' not in _dict.keys():
            _dict['switch'] = False

        if 'switch_action' not in _dict.keys():
            _dict['switch_action'] = True

        if 'type' not in _dict.keys():
            _dict['type'] = 'str'

    return arg_dict
