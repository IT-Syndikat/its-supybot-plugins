# -*- coding: utf-8 -*-
###
# Copyright (c) 2013, d.prskavec
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from random import choice
import re

class Stuff(callbacks.Plugin):
    """Random small stuff"""
    


    def _nickInsert(self, text, nick):
        """replaces ich/mich/mein by calling nick"""
        text = re.sub(r'\bich(\b|[,.!?;:])', nick, text)
        text = re.sub(r'\bmich(\b|[,.!?;:])', nick, text)
        text = re.sub(r'\bmein(\b|[,.!?;:])', nick+'\'s' ,text)
        text = re.sub(r'\bmir(\b|[,.!?;:])', nick, text)
        return text

    def wer(self, irc, msg, args, channel, text):
        """[<channel>] <text>

        sagt wer's war, ist oder gewesen sein wird"""

        if irc.isChannel(msg.args[0]) == False:
            if irc.isChannel(channel) == False:
                irc.reply("Du musst einen validen channel angeben")
            else:
                nick = choice([str(x) for x in irc.state.channels[channel].users])
                resp = nick +' '+ self._nickInsert(text,msg.nick)
                irc.reply(resp.strip('?,.!;:') + '.', prefixNick=False) 
            return
        else:
            nick = choice([str(x) for x in irc.state.channels[msg.args[0]].users])
            resp = nick +' '+ self._nickInsert(text,msg.nick)
            irc.reply(resp.strip('?,.!;:') + '.', prefixNick=False)
        return
    wer = wrap(wer, [optional('channel'), 'text'])

    
#    def langweilig(self, irc, msg, args):
#        """takes no arguments
#
#        vermindert langeweile ... NICHT!"""
#        replies = [ u'Lies ein Buch!'.encode('utf-8'), 
#                    u'Räum dein Zimmer auf!'.encode('utf-8'),
#                    u'Lauf eine Runde um den Block!'.encode('utf-8'),
#                    u'Mach deine Hausaufgaben!'.encode('utf-8'),
#                    u'Schreib mir ein neues Plugin!'.encode('utf-8')
#                    ];
#        snark = choice(replies)
#        irc.reply(choice(replies), prefixNick=True) 
#        return
    

Class = Stuff


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
