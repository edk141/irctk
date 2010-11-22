from collections import defaultdict

cmd_hooks = {} # store functions in a standard dictionary
sub_hooks = defaultdict(list) # store functions in a list associated with a hook

def command(hook=None):
    '''Associate a command hook with a function. Uses cmd_hooks dict.'''

    def command_wrapper(func):
        if hook in cmd_hooks or not hook and func.func_name in cmd_hooks:
            raise ValueError('Duplicate command hook found.')
        
        if hook:
            cmd_hooks[hook] = func
        else:
            cmd_hooks[func.func_name] = func
        
        return func
    
    if hook:
        return command_wrapper
    else:
        return command_wrapper(hook)

def subscribe(hook):
    '''Subscribe a function to an event. Uses sub_hooks dict.'''

    def subscribe_wrapper(func):
        sub_hooks[hook].append(func)
        return func
    
    return subscribe_wrapper

def handle(bot, event):
    return Handler(bot, event)

class Handler(object):
    '''Determines if an event is directed to subscriptions or commands. 
       Either prefixed with bot.irc.nick or bot.cmd_prefix.
    '''

    def __init__(self, bot, event):
        self.bot = bot
        self.event = str(event.args.trailing) # unicode breaks
        self._dispatch(bot, event, self._is_command(), self._is_prefix())

    def _is_command(self): 
        return self.event.startswith(self.bot.irc.nick)

    def _is_prefix(self):
        return self.event.startswith(self.bot.cmd_prefix)

    def _dispatch(self, bot, event, is_cmd, is_pre):
        '''Dispatch hooks in respone to events. Nick prefixed or prefixed,
           is_cmd and is_pre respectively.
        '''
        
        trl = event.args.trailing

        if is_cmd:
            try:
                func = cmd_hooks[trl.split(': ')[1].split()[0]]
                func(bot, event.args)
            except KeyError:
                pass
            except IndexError:
                pass
        elif is_pre:
            try:
                func = cmd_hooks[trl.split()[0].split(bot.cmd_prefix)[-1]]
                func(bot, event.args)
            except KeyError:
                pass
            except IndexError:
                pass
        else:
            for func in sub_hooks[event.hook]:
                func(bot, event.args)