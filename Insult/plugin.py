###
# Copyright (c) 2005, Daniel DiPaolo, 2013 Detlef Prskavec (praise->insult)
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

import re

from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils

class Insult(plugins.ChannelIdDatabasePlugin):
    """Insult is a plugin for ... well, insulting things.  Feel free to add
    your own flavor to it by customizing what insults it gives.  Use "insult
    add <text>" to add new ones, making sure to include "$who" in <text> where
    you want to insert the thing being insulted.
    """
    _meRe = re.compile(r'\bme\b', re.I)
    _myRe = re.compile(r'\bmy\b', re.I)
    _ichRe = re.compile(r'\bich\b', re.I)
    _michRe = re.compile(r'\bmich\b', re.I)
    _meinRe = re.compile(r'\bmein\n', re.I)

    def _replaceFirstPerson(self, s, nick):
        s = self._meRe.sub(nick, s)
        s = self._myRe.sub('%s\'s' % nick, s)
        s = self._ichRe.sub(nick, s)
        s = self._michRe.sub(nick, s)
        s = self._meinRe.sub('%s\'s' % nick, s)
        return s

    def addValidator(self, irc, text):
        if '$who' not in text:
            irc.error('Insults must contain $who.', Raise=True)

    def insult(self, irc, msg, args, channel, id, text):
        """[<channel>] [<id>] <who|what> [for <reason>]

        Insults <who|what> (for <reason>, if given).  If <id> is given, uses
        that specific insult.  <channel> is only necessary if the message isn't
        sent in the channel itself.
        """
        if ' for ' in text:
            (target, reason) = map(str.strip, text.split(' for ', 1))
        else:
            (target, reason) = (text, '')
        if ircutils.strEqual(target, irc.nick):
            target = 'itself'
        if id is not None:
            try:
                insult = self.db.get(channel, id)
            except KeyError:
                irc.error(format('There is no insult with id #%i.', id))
                return
        else:
            insult = self.db.random(channel)
            if not insult:
                irc.error(format('There are no insults in my database ' \
                                 'for %s.', channel))
                return
        text = self._replaceFirstPerson(insult.text, msg.nick)
        reason = self._replaceFirstPerson(reason, msg.nick)
        target = self._replaceFirstPerson(target, msg.nick)
        text = text.replace('$who', target)
        if reason:
            text += ' for ' + reason
        if self.registryValue('showIds', channel):
            text += format(' (#%i)', insult.id)
        irc.reply(text, prefixNick=False, action=False)
    insult = wrap(insult, ['channeldb', optional('id'), 'text'])

Class = Insult

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
