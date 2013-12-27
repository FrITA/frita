#FrITA - Free Interactive Text Aligner

            # Copyright (C) 2013 Gregory Vigo Torres

            # This program is free software: you can redistribute it and/or modify
            # it under the terms of the GNU General Public License as published by
            # the Free Software Foundation, either version 3 of the License, or
            # any later version.

            # This program is distributed in the hope that it will be useful,
            # but WITHOUT ANY WARRANTY; without even the implied warranty of
            # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
            # GNU General Public License for more details.

            # You should have received a copy of the GNU General Public License
            # along with this program. If not, see http://www.gnu.org/licenses/.

## Parses rules from an sqlite database of segmentation rules
## and segments a list of paragraphs into sentences.

import sqlite3 as sqlite
import re
import config

class parse_rules():
    def __init__(self, rulesdb, lang):
        self.rulesdb = sqlite.connect(rulesdb)
        # test if lang is in db
        lang_tables = self.rulesdb.execute("SELECT name FROM sqlite_master;")
        all_langs = lang_tables.fetchall()
        all_langs = [i[0] for i in all_langs]
        self.break_rules = []
        self.skip_rules = []
        lang = lang.split()[0]
        self.error = False

        if lang not in all_langs:
            self.error = True
            def_break_rules = self.get_rules('dflt', '1')
            def_skip_rules = self.get_rules('dflt', '0')

            for r in def_break_rules:
                self.break_rules.append(r)

            for r in def_skip_rules:
                self.skip_rules.append(r)

        else:
            break_rules = self.get_rules(lang, '1')
            skip_rules = self.get_rules(lang, '0')

            # get dflt rules
            def_break_rules = self.get_rules('dflt', '1')
            def_skip_rules = self.get_rules('dflt', '0')

            for r in def_break_rules:
                self.break_rules.append(r)

            for r in break_rules:
                self.break_rules.append(r)

            for r in def_skip_rules:
                self.skip_rules.append(r)

            for r in skip_rules:
                self.skip_rules.append(r)

        self.rulesdb.close()

    def get_rules(self, lang, brk):
        cmd = "SELECT before FROM "+lang+" WHERE break ='"+brk+"'"
        b = self.rulesdb.execute(cmd)
        before = b.fetchall()
        before = [i[0] for i in before]

        cmd = "SELECT after FROM "+lang+" WHERE break ='"+brk+"'"
        a = self.rulesdb.execute(cmd)
        after = a.fetchall()
        after = [i[0] for i in after]

        if len(before) == len(after):
            rules = zip(before, after)

        return rules

class segment():
    def __init__(self, break_rules, skip_rules, raw_text):

        self.segmented_text = []
        self.skip_rules = skip_rules
        self.break_rules = break_rules

        for line in raw_text:
            if line.isspace() == False and line != '\n':
                self.segment_line(line.strip() )

    def output_segments(self, segmented_line):
        self.segmented_text.extend(segmented_line)

    def get_breaks(self, line):
        break_points = []
        for r in self.break_rules:
            pattern = '('+r[0]+')('+r[1]+')'
            matchobjs = re.finditer(pattern, line)
            for i in matchobjs:
                break_points.append(i.end() )

        re.purge()
        return break_points

    def get_skips(self, line):
        skip_points = []
        for r in self.skip_rules:
            pattern = '('+r[0]+')('+r[1]+')'
            matchobjs = re.finditer(pattern, line)
            for i in matchobjs:
                skip_points.append(i.end() )

        re.purge()
        return skip_points

    def segment_line(self, line):
        real_breaks = []
        segmented_line = []

        allnumbers = re.search('[a-zA-Z]', line)
        if allnumbers is None:
            segmented_line.append(line)
            self.output_segments(segmented_line)
            return None

        brks = re.search('[\.?!]', line)
        if brks is None:
            segmented_line.append(line)
            self.output_segments(segmented_line)
            return None

        break_points = self.get_breaks(line)
        skip_points = self.get_skips(line)

        if len(break_points) > 0:
            start = 0
            for brk in break_points:
                if brk not in skip_points:
                    real_breaks.append(brk)
                    seg = line[start:brk]
                    segmented_line.append(seg)
                    start = brk

                    if start == break_points[-1]:   # get last part
                        seg = line[start:]
                        segmented_line.append(seg)

        else:   # no breaks in line
            segmented_line.append(line)

        self.output_segments(segmented_line)

