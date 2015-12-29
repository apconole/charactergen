#!/usr/bin/env python
#

import os
import utils
import random

class background(object):
    class package(object):
        def __init__(self, name, charclass, background, stat, intelligence, wisdom, constitution, dexterity, charisma, primary_stat):
            self._name = name.lower()
            self._charclass = charclass
            self._background = background
            self._strength = stat
            self._intelligence = intelligence
            self._wisdom = wisdom
            self._constitution = constitution
            self._dexterity = dexterity
            self._charisma = charisma
            self._primary_stat = primary_stat

        def name(self):
            return self._name

        def is_name(self, name):
            return self._name == name.lower()

        def charclass(self):
            return self._charclass

        def background(self):
            return self._background

        def rand_strength(self):
            stat = self._strength
            return utils.gen_stat(stat[0], stat[1], stat[2])

        def rand_intelligence(self):
            stat = self._intelligence
            return utils.gen_stat(stat[0], stat[1], stat[2])

        def rand_wisdom(self):
            stat = self._wisdom
            return utils.gen_stat(stat[0], stat[1], stat[2])

        def rand_dexterity(self):
            stat = self._dexterity
            return utils.gen_stat(stat[0], stat[1], stat[2])

        def rand_constitution(self):
            stat = self._constitution
            return utils.gen_stat(stat[0], stat[1], stat[2])

        def rand_charisma(self):
            stat = self._charisma
            return utils.gen_stat(stat[0], stat[1], stat[2])

        def primary_stat(self):
            return self._primary_stat
    
    def __init__(self, canonicalName):
        self._canonical_name = canonicalName
        self._given_names = []
        self._given_names_gender = []
        self._sur_names = []
        self._packages = []
        self.currency = 'unknown'
        self.currency_exchange = 0
        self._load_background()

    def _load_background_from_db(self):
        raise Exception("DB support not implemented")

    def _load_background_from_file(self):

        for path_lookup in utils.get_paths():
            background_hnd = path_lookup + self._canonical_name + '.xml'
            print "checking '%s'" % background_hnd
            if os.path.exists(background_hnd):
                break
            background_hnd = None

        if background_hnd is None:
            raise Exception("Background '%s' not found" + self._canonical_name)
        background_root = utils.read_xml_data(background_hnd)
        if background_root.tag.lower() != 'background':
            raise Exception("Background '%s' has invalid root tag '%s'" % (self._canonical_name, background_root.tag))

        for child in background_root:
            if child.tag.lower() == 'surname':
                self._add_surname(child.text)
            if child.tag.lower() == 'givenname':
                gender='either'
                self._add_givenname(child.text, gender)
            if child.tag.lower() == 'name':
                if child.attrib['type'] == 'sur':
                    self._add_surname(child.text)
                elif child.attrib['type'] == 'given':
                    gender='either'
                    self._add_givenname(child.text, gender)
                else:
                    raise Exception("ambiguous name. check the type attribute")
            elif child.tag.lower() == 'currency':
                self.currency = child.text
                self.currency_exchange=float(child.attrib.get('exchange','1.0'))
            elif child.tag.lower() == 'description':
                self.description = child.text
            elif child.tag.lower() == 'sur':
                pkgname = child.attrib.get('name')
                for package in child.findall('package'):
                    pkgclass = package.find('class').text
                    pkgbg = package.find('background').text
                    pkgattribs = {}
                    pkgattribs['primary'] = ' '
                    for ability in ['str', 'int', 'wis', 'con', 'dex', 'cha']:
                        pkgability = package.find(ability)
                        pkgability_mod = 0
                        pkgability_floor = 3
                        pkgability_ceiling = 18
                        if pkgability is not None:
                            pkgability_mod = pkgability.text
                            pkgability_floor = int(pkgability.attrib.get('floor', '3'))
                            pkgability_ceiling = int(pkgability.attrib.get('ceiling', '18'))
                            if int(pkgability.attrib.get('primary', 0)) == 1:
                                pkgattribs['primary'] = ability

                        pkgattribs[ability] = [pkgability_mod, pkgability_floor, pkgability_ceiling ]

                    self._packages.append(background.package(pkgname, pkgclass, pkgbg, pkgattribs['str'], pkgattribs['int'], pkgattribs['wis'], pkgattribs['con'], pkgattribs['dex'], pkgattribs['cha'], pkgattribs['primary']))
            else:
                print "Ignoring tag '%s'" % child.tag

    def _add_surname(self, name):
        self._sur_names.append(name)

    def _add_givenname(self, name, gender):
        self._given_names.append(name.lower())
        self._given_names_gender.append(gender.lower())

    def _load_background(self):
        if os.getenv("SCRIPT_NAME"):
            self._load_background_from_db()
        else:
            self._load_background_from_file()

    def _get_package(self, surname):
        choices = [x for x in self._packages if x.is_name(surname)]

        if len(choices) == 0:
            raise Exception("Surname %s not defined" % surname)
        
        selected = random.choice(choices)

        return selected.charclass(), selected.background(), selected.rand_strength(), selected.rand_intelligence(), selected.rand_wisdom(), selected.rand_constitution(), selected.rand_dexterity(), selected.rand_charisma(), selected.primary_stat()
            
    def random_name(self):
        return random.choice(self._given_names).capitalize() + ' ' + random.choice(self._sur_names).lower().capitalize()
    
    def gender_from_name(self, name):
        given, sur = utils.get_names(name)
        pos = self._given_names.index(given.lower())

        return self._given_names_gender[pos]

    def _print_two_stats(self, statone, statoneval, stattwo, stattwoval, primary):
        etc = ""
        if primary != statone and primary != stattwo:
            etc += " %s : %02d [%+1d]           %s : %02d [%+1d]\n" % (statone.capitalize(), statoneval, utils.get_stat_modifier(statoneval), stattwo.capitalize(), stattwoval, utils.get_stat_modifier(stattwoval))
        else:
            if primary == statone:
                etc += "*%s*: %02d [%+1d](+%02d%% XP)  %s : %02d [%+1d]\n" % (statone.capitalize(), statoneval, utils.get_stat_modifier(statoneval), utils.stat_xp_percent(statoneval), stattwo.capitalize(), stattwoval, utils.get_stat_modifier(stattwoval))
            else:
                etc += " %s : %02d [%+1d]          *%s*: %02d [%+1d](+%02d%%)\n" % (statone.capitalize(), statoneval, utils.get_stat_modifier(statoneval), stattwo.capitalize(), stattwoval, utils.get_stat_modifier(stattwoval), utils.stat_xp_percent(stattwoval))
        return etc

    def _json_stat(self, statname, statval):
        return "         {\"name\": \"%s\", \"value\": \"%02d\", \"modifier\": \"%+1d\"}" % (statname.capitalize(), statval, utils.get_stat_modifier(statval))
    
    def random_char(self, printable=True):
        NewChar = self.random_name()
        given, sur = utils.get_names(NewChar)

        gender = self.gender_from_name(NewChar)

        if gender == "either":
            gender = random.choice(["male", "female"])

        if gender == "male":
            opronoun = "his"
            pronoun = "he"
        else:
            pronoun = "she"
            opronoun = "her"
        
        PackageClass, PackageBG, PackageStr, PackageInt, PackageWis, PackageCon, PackageDex, PackageCha, PrimaryStat = self._get_package(sur)
        bgstr = "%s the %s %s %s\n" % (NewChar, PackageClass, utils.background_from(), PackageBG.replace('$name', NewChar).replace('$gender', gender).replace('. $pronoun', '. ' + pronoun.capitalize()).replace('$pronoun', pronoun).replace('. $opronoun', '. ' + opronoun.capitalize()).replace('$opronoun', opronoun))
        gold = utils.gen_stat(0) * 10 * self.currency_exchange
        if printable:
            returnval = "Name: %s\n" % NewChar
            returnval += "Gender: %7s    Class: %s    Primary: %s\n" % (gender, PackageClass, PrimaryStat)

            returnval += self._print_two_stats('str', PackageStr, 'int', PackageInt, PrimaryStat)
            returnval += self._print_two_stats('wis', PackageWis, 'con', PackageCon, PrimaryStat)
            returnval += self._print_two_stats('dex', PackageDex, 'cha', PackageCha, PrimaryStat)
            returnval += "Starting gold (based on %s exchange): %s\n" % (self.currency, gold)
            returnval += "----------------------\n"
            returnval += bgstr
            return returnval
        returnval = "{\n"
        returnval += "  \"character\": {\n"
        returnval += "    \"name\": \"%s\",\n" % NewChar
        returnval += "    \"gender\": \"%s\",\n" % gender
        returnval += "    \"class\": \"%s\",\n" % PackageClass
        returnval += "    \"primary_stat\": \"%s\",\n" % PrimaryStat
        returnval += "    \"starting_gold\": \"%f\",\n" % gold
        returnval += "    \"background\": \"%s\",\n" % bgstr
        returnval += "    \"statblock\": {\n"
        returnval += "       \"stat\": [\n"
        returnval += self._json_stat('str', PackageStr) + ",\n"
        returnval += self._json_stat('int', PackageInt) + ",\n"
        returnval += self._json_stat('wis', PackageWis) + ",\n"
        returnval += self._json_stat('con', PackageCon) + ",\n"
        returnval += self._json_stat('dex', PackageDex) + ",\n"
        returnval += self._json_stat('cha', PackageCha) + "\n"
        returnval += "       ]\n"
        returnval += "    }\n"
        returnval += "  }\n"
        returnval += "}\n"
        return returnval
