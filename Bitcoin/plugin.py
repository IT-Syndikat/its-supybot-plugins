###
# Copyright (c) 2013, detlef prskavec
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

import os
import datetime
import urllib2
import simplejson
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.log as log


class Bitcoin(callbacks.Plugin):
    """This plugin checks the current market price of BTC on
    the given market. It queries http://bitcoincharts.com
    usage: !btc <market> <currency>"""
    threaded = True

    def _fetchJsonData(self):
        """fetches jsondata from url"""
        url = 'http://bitcoincharts.com/t/markets.json'
        ua = {'user-agent':'supybot-plugin/Bitcoin'}
        req = urllib2.Request(url, None, ua)
        f = urllib2.urlopen(req)
        data = simplejson.load(f)
        return data     

    def _writeToFile(self, data, filename):
        """writes the json data to file"""
        f = open(filename, 'w')
        f.write(str(data))
        f.flush()
        f.close()

    def _readFromFile(self,filename):
        """reads the jsondata from file"""
        if os.path.exists(filename):
            f = open(filename, 'r')
            data = simplejson.load(f)
            return data
        else:
            raise Exception('data file not found')

    def _getLastEntry(self, channel):
        """fetche the json data from either a file stored from the
        last request (only 1 request per 15 minutes allowed) or
        makes a new request and stores the result in a file as well
        """
        filename = plugins.makeChannelFilename('bitcoin', channel)
        # if file older than 15 minutes -> new query
        if os.path.exists(filename) == True:
            delta = datetime.timedelta(minutes=15)
            statbuf = os.stat(filename)
            now = datetime.datetime.now()
            modtime = datetime.datetime.fromtimestamp(statbuf.st_mtime) 
            if (now - delta) > modtime:
                data = self._fetchJsonData()
                self._writeToFile(simplejson.dumps(data), filename)
                log.info('new data')
                return simplejson.dumps(data)
            else:
                data = self._readFromFile(filename)
                log.info('old data')
                return  simplejson.dumps(data)
        else:
            data = self._fetchJsonData()
            self._writeToFile(simplejson.dumps(data), filename)     
            log.info('create new file and new data')
            return data


    def _fetchAllSymbols(self, data):
        """fetches all symbols that are in the data"""
        dlist = simplejson.loads(data)
        symList = []
        for item in dlist:
            symList.append(item['symbol'])
        return symList;


    def _fetchLastTrade(self, data, sym):
        """fetches the price of the last trade at market
            <symbol>"""

        dlist = simplejson.loads(data)
        for item in dlist:
            if item['symbol'] == sym:
                return {"time":item['latest_trade'],
                        "value":item['close'],
                        "currency":item['currency']}
        return None


    def symbols(self, irc, msg, args):
        """takes no arguments

        Lists all symbols of the markets for which we have data
        """
        if irc.isChannel(msg.args[0]) == True:
            channel = msg.args[0]
            json = self._getLastEntry(channel)
            irc.reply(str(self._fetchAllSymbols(json)))
        else:
            irc.reply('bitcoin query can only be called from a channel.')


    def query(self, irc, msg, args, symbol):
        """<symbol>

        Fetches the value of last trade of market defined by <symbol>
        """
        if symbol is not None:
            if irc.isChannel(msg.args[0]) == True:
                channel = msg.args[0]
                json = self._getLastEntry(channel)
                res = self._fetchLastTrade(json, symbol)
                if res is not None:
                    date = datetime.datetime.fromtimestamp(res['time'])
                    amount = res['value']
                    cur = res['currency']
                    irc.reply(symbol+': '+ str(amount)+cur+' ('+str(date)+')')
                else:
                    irc.reply('no data for '+symbol)
            else:
                irc.reply('bitcoin query can only be called from a channel.')
        else:
            irc.reply('enter a symbol (e.g. mtgoxEUR)')
    query = wrap(query, ['text'])   

    def convert(self, irc, msg, args, amount, currency):
        """<amount> [<currency>]

        converts amount of currency to bitcoin. using the default
        markets. currently works for USD and EUR. if no currency
        is given it defaults to EUR
        """
        defaultMarkets = { "EUR":"btc24EUR", "USD":"mtgoxUSD" }
        if currency is None:
            currency = "EUR"

        if irc.isChannel(msg.args[0]) == True:
            symbol = defaultMarkets[currency]
            if symbol is None:
                reply = "currency unsupported. supported currencies are: "
                reply = reply + str(defaultMarkets.keys())
                irc.reply(reply, prefixNick=True)
            channel = msg.args[0]
            json = self._getLastEntry(channel)
            res = self._fetchLastTrade(json, symbol)
            if res is not None:
                rate = res['value']
                reply = str(amount) + " " + currency + " = "
                reply = reply + str(amount / float(rate)) + " BTC"
                irc.reply(reply, prefixNick=True)
            else:
                irc.reply('no data for '+symbol, prefixNick=True)
        else:
            irc.reply('bitcoin query can only be called from a channel.')
    convert = wrap(convert, ['float', optional('text', 'EUR')])

Class = Bitcoin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
