#!/usr/bin/env python
'''
Pre/post procesor for kicad & ngspice v jupyter notebooku

'''

import os, sys, re
from numpy import *
from raw import *


class kSim(): 
    '''
    Pomocna trieda pre riadenie simulacie
    
    Funkcie:
        - uprava netlistu pre simulator ngspice, doplnenie modelov
          a atributov pre blokove komponenty XSPICE
        - spustenie simulacie
        - konverzia vysledkov simulacie do datovych struktur Pythonu
    '''

    def __init__(self, netlist_name):
        '''
        Inicializacia vstupnych parametrov simulacie.

        Args:
            filename:  meno suboru *.sch z editora gschem 
        '''
                            # public variables
        self.xData=[]       # independent simulation x-variable (time, frequency)     
        self.yData={}       # list of variables extracted from *.raw data
        
                            # private variables
        self._filename=''   # simulator input filename
        self._c_list=[]     # zoznam komponentov schemy
        self.models={}      # slovnik pouzitych modelov v netliste

        self._filename = netlist_name
    

    def netlist(self):
        '''
        Kontrolne nacitanie netlistu
        '''
        fp=open(self._filename)
        lines = fp.readlines()
        fp.close()
        
        ret_val = ''.join(lines)
        return ret_val
        
        
    def setDC(self, srcName, start, stop, incr):
        '''
        Nastavenie .DC analyzy v interaktivnom mode. Prepise existujuci 
        prikaz v netliste.
        
        Definuje parametre .DC simulácie. Je ekvivalentom direktívy 
        .DC použitej v netliste.
        
        Args:
            srcName:  meno zdroja, string
            vstart:   pociatocna hodnota
            vstop:    koncova hodnota
            vincr:    inkrement hodnoty
        '''
        find   =r'.DC\s+'
        replace=r'.DC ' + srcName + ' ' + str(start)+' ' +str(stop)+' '+str(incr) + '\n'
        self.findAndReplace(find, replace)
        

    def setAC(self, start, stop, number=100, stype='DEC' ):
        '''
        Nastavenie .AC analyzy v interaktivnom mode. Prepise existujuci
        prikaz v netliste.
        
        Definuje parametre small signal .AC simulácie. Je ekvivalentom direktívy 
        .AC použitej v netliste.
        
        Args:
            start:  počiatocna frekvencia [float]
            stop:   koncova frekvencia [float]
            number: pocet bodov v intervale simulácie (optional) [int]
            stype:  typ delenia frekvencneho rozsahu [str] ('DEC', 'OCT', 'LIN') 
        '''
        if start >= stop:
            print ("Error in .AC command")
            print ("    Start freg > stop freq")
            return
            
        if stype in ['DEC', 'LIN', 'OCT']:
            pass
        else:
            print ("Error in .AC parameters")
            print ("    Parameter stype must be one of LIN, DEC or OCT")
            return
                    
        find   =r'.AC\s+'
        replace=r'.AC '+stype+' '+str(number)+' '+str(start)+' '+str(stop)+'\n'
        self.findAndReplace(find, replace)
        
        
    def setTRAN(self, tstep, tstop, tstart=0, tmax=0, uic='' ):
        '''
        Nastavenie .TRAN analyzy v interaktivnom mode. Prepise existujuci
        prikaz v netliste.
        
        Definuje parametre .TRAN simulácie. Je ekvivalentom direktívy 
        .TRAN použitej v netliste.
        
        Args:
            tstep: časový krok simulácie pre generovanie výstupu
            tstop: koniec čas simulácie
            tstart: počiatočný čas simulácie pre generovania výstupu
            tmax: maximálna veľkosť kroku 
            uic: použitie počiačných podmienok ['', 'UIC']
        '''
        find   =r'.TRAN\s+'
        replace=r'.TRAN '+str(tstep)+' '+str(tstop)+' ' +str(tstart)+' '+str(tmax)+' '+uic+'\n'
        self.findAndReplace(find, replace)
                    

    def setPAR(self, parName, parValue):
        '''
        Doplnie a modifikácia prametrov pomocou príkazu .PARAMS v netliste. 
        
        Definovanie hodnôt symbolických parametrov v netliste pomocou prikazu .PARAMS.
        Ak je už parameter definovaný, jeho hodnota sa prepíše.  
        Pre kazdy parameter sa generuje samostatny prikaz .PARAMS.
        
        Args:
            parName: meno parametra [str]
            parValue: hodnota parametra [int, float, str]
        '''   
        find   =r'.PARAM\s+'+parName
        replace=r'.PARAM '+parName+'='+str(parValue)+'\n'
        self.findAndReplace(find, replace)
        

    def setOPT(self, parName, parValue):
        '''
        Doplni parametrov simulácie do netlistu pomocou parametra .OPTIONS.
        
        Predchadzajuce prikazy .OPTIONS prepíše. Pre kazdy parameter 
        generuje samostatny prikaz .OPTIONS.
        '''     
        find   =r'.OPTIONS\s+'+parName
        replace=r'.OPTIONS '+parName+'='+str(parValue)+'\n'
        self.findAndReplace(find, replace)
        
    def setMODEL(self, modName, params):
        '''
        Doplnenie a definovanie simulačného modelu do netlistu.
        
        Args:
            modName: meno modelu (str)
            params:  parametre modelu v reťazci (str)
        '''
        find   =r'.MODEL\s+' + modName
        replace=r'.MODEL '+ modName + ' ' + params + '\n'
        self.findAndReplace(find, replace)
        
    def setPROBE(self, nodeList):
        '''
        Definovanie zoznamu uzlov pre generovanie
        vystupu simulacie. Bez zadania generuje vystup pre vsetky uzly
        zapojenia.
        
        Args:
            nodeList: zoznam uzlov
        '''
        s = ''
        for i in nodeList:
            s = s + str(i) + ' '
        
        # TODO - upravit na self.appendNetlist() ...
        find   =r'.PROBE 123456789ABCDEFG\s+' 
        replace=r'.PROBE '+ s + '\n'
        self.findAndReplace(find, replace)
        
    def setCOMP(self, compName, nodeList, compValue):
        '''
        Doplnenie komponentu do netlistu a/alebo zmena jeho parametrov. 
        
        Doplnenie komponentu do netlistu alebo zmena parametrov existujúceho
        komponentu.
        
        Args:
            compName: meno komponentu (str)
            nodeList: zoznam uzlov pripojenia komponentu ([str, str ..])
            compValue: hodnota komponentu (str)
        '''   
        s = ' '
        for i in nodeList:
            s = s + str(i) + ' '
             
        find   = compName + r'\s+'
        replace= compName + s + str(compValue) + '\n'
        self.findAndReplace(find, replace)
        
        # Obnovenie netlistu po zmene konfiguracie komponentu
        # Po zmene parametrov (zadanie noveho modelu) je potrebne 
        # vyhladat a nacitat modely komponentov.
        
        # WARNING - pouzitie convert kazi komponenty A
        
        conv = gnetConvert(self._filename, self._filename, self._c_list, self.models)
        ret_val = conv.convert()
        
        return ret_val
        
    def setVALUE(self, compName, value):
        '''
        Nahradenie posledneho argumentu v deklaracii komponentu, predpokladá 
        ako posledný argument hodnotu value.
        
        Pre komponenty s atributom value obsahujucim model komponentu zmaze 
        riadok s .INCLUDE stareho modelu a vyradi model zo slovnika self.models
        
        Vola metodu convert(), ktora obnovi zoznam modelov a ich .INCLUDE 
        '''
        # TODO kontrola na existenciu netlistu
        
         # povodny subor s netlistom, vyhladanie riadku s komponentom v netliste
        inputFile = open(self._filename+'.net', "r")
        while True:
            line = inputFile.readline()    # citanie suboru po riadkoch
            if line.find(compName) !=-1:   # aktualny riadok s najdenym menom komponentu
                break
            if line == '':                 # koniec suboru
                break
        inputFile.close() 
        
        # compName nenajdene, TODO - osetrenie stavu, chybove hlasenie, nekonzistentny netlist
        if line == '':
            return ''
        
        # uprava formatu riadku, odstranenie white sapace zlava, sprava
        line = line.rstrip()
        line = line.lstrip()
        
        # rozdelenie riadku s komponentom na polozky podla oddelovaca - medzera
        q = line.split(' ')
        old_value = q[-1]         # posledna polozka q[-1]-> povodna hodnota atributu value
        
        # osetrenie chyby, opakovana rovnaka zmena hodnoty
        if old_value == value:
            return ''
            
        q[-1] = value      # zamena starej hodnoty na novu
        
        # poskladanie noveho retazca s definiciou komponentu
        newStr = ''
        for i in q:
            newStr = newStr + str(i) + ' '
        newStr = newStr + '\n'
        
        #---------------------------------------------------------------
        # nacitanie povodneho netlistu do jedneho textoveho bloku
        inputFile = open(self._filename, "r")
        lines = inputFile.read()
        inputFile.close()
        
        # uprava suboru, vyhladanie a zamena riadku, line obsahuje povodny riadok, newStr obsahuje upraveny riadok
        update = lines.replace(line, newStr)
        
        # zapis upraveneho netlistu
        outputFile=open(self._filename,"w+")
        outputFile.write(update)
        outputFile.close()
        
        #---------------------------------------------------------------
        # pre komponenty, ktore obsahuju v atribute value model komponetu
        # zmazanie stareho modelu z databazy a zrusenie jeho INCLUDE
        # pre standardne komponenty s numerickou alebo symbolickou hodnotou atributu value 
        # je nasledujuci blok try-except ignorovany
        try:
            self.findAndReplace(r'.INCLUDE\s'+self.models[old_value], '*\n')
            del self.models[old_value]
        except KeyError:
            pass
        
        # aktualizacia v pripade vymeny modelu pre komponenty s modelom (Q,D,X ...)
        # a doplnenie INCLUDE aktualnych modelov 
        conv = gnetConvert(self._filename, self._filename, self._c_list, self.models)
        ret_val = conv.convert()
        
        return ret_val
        
      
    def sim(self, log = True):
        '''
        Metoda spusti simulaciu a konvertuje data z raw suboru.

        Hodnoty z *.raw súboru sú po simulácii konvertované do dátových
        štruktúr Pythonu.
        '''
        # zmazanie stareho raw suboru
        try:
            os.remove(self._filename + '.raw')
        except OSError as error:
            pass
        
        if log==False:
            cmd="ngspice -b -a "+self._filename+" -r "+self._filename+".raw" # 
        else:
            cmd="ngspice -b -a "+self._filename+" -r "+self._filename+".raw > log.txt "
        os.system(cmd)
        
        if not os.path.isfile(self._filename+".raw"):
            print ("Error in simulation, check netlist")
            print ("    Output file "+self._filename+".raw not created")
            return False
            
        # vyhladanie a konverzia dat v RAW subore
        #varlist = raw.spice_read(self._filename+".raw").get_plots()
        varlist = spice_read(self._filename+".raw").get_plots()
        pl=varlist[0]

        # hodnoty x-osi - nezavisla premenna 
        self.xData= pl.get_scalevector().get_data()

        self.yData={}                           # mena premennych a data z raw suboru
        for v in pl.get_datavectors():          # konverzia do slovnika
            self.yData[v.name.lower().strip()]=v.get_data()
        return True
        
        
    def findAndReplace(self, strFind, strReplace):
        '''
        Uprava a doplnenie záznamu do netlistu.
        
        Vyhladanie existujuceho parametra v subore s netlistom 
        a nahradenie s novymi hodnotami. Ak sa parameter v netliste nevyskytuje, 
        doplnenie do netlistu pred direktívu .END.
        
        Args:
            strFind: reťazec pre vyhladanie (meno parametra a pod.) [str]
            strReplace: reťazec pre nahradenie (parameter a hodnoty) [str]
        '''
        try:
            inputFile = open(self._filename, "r")
            lines = inputFile.readlines()
            inputFile.close() 
                    
            outputFile=open(self._filename,"w+")

        except:
            print ('>>> Error open netlist file '+self._filename)
            return False

        # prehladanie netlistu po riadkoch, hladanie retazca strFind
        # a prepisanie retazcom strReplace   
        
        parFound = False
        endFound = False
        for idx, s in enumerate(lines):
            if re.match(strFind, s)!=None:  # hladanie exaktneho tvaru
                parFound=True
                lines[idx] = strReplace     # ak existuje, prepis parametra
                break

        # zapis do suboru, kontrola posledneho riadku
        for s in lines:
            if re.match(r'.END', s.upper()) != None:
                endFound = True
                # doplnenie parametra pred .END
                if parFound==False:
                    outputFile.write(strReplace)   # ak neexistuje, doplnenie parametra
            outputFile.write(s)                    # zapis s -> END posledny najdeny retazec
        outputFile.close()
        
        # chybajuci .END na konci netlistu
        if endFound is False:
            print('>>> Error in netlist - missing .END directive')
            # TODO doplnit END
        return True
        

