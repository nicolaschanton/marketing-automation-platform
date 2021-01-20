# -*- coding: utf-8 -*-

from please_marketing_growth_hack.models import BaseSiren
import requests
from django.conf import settings
import json
import sys
from concurrent.futures import ThreadPoolExecutor
import csv

# MaJ Mensuelle : http://files.data.gouv.fr/sirene/sirene_201807_M_M.zip


def import_stock_file(filereader_list):
    for row in filereader_list:
        print(row)
        if row[0] == 'SIREN':
            print('First Line')
        else:
            if BaseSiren.objects.filter(siren=row[0]).count() == 0:
                BaseSiren(
                    siren=row[0],
                    nic=row[1],
                    l1_normalisee=row[2],
                    l2_normalisee=row[3],
                    l3_normalisee=row[4],
                    l4_normalisee=row[5],
                    l5_normalisee=row[6],
                    l6_normalisee=row[7],
                    l7_normalisee=row[8],
                    l1_declaree=row[9],
                    l2_declaree=row[10],
                    l3_declaree=row[11],
                    l4_declaree=row[12],
                    l5_declaree=row[13],
                    l6_declaree=row[14],
                    l7_declaree=row[15],
                    numvoie=row[16],
                    indrep=row[17],
                    typvoie=row[18],
                    libvoie=row[19],
                    codpos=row[20],
                    cedex=row[21],
                    rpet=row[22],
                    libreg=row[23],
                    depet=row[24],
                    arronet=row[25],
                    ctonet=row[26],
                    comet=row[27],
                    libcom=row[28],
                    du=row[29],
                    tu=row[30],
                    uu=row[31],
                    epci=row[32],
                    tcd=row[33],
                    zemet=row[34],
                    siege=row[35],
                    enseigne=row[36],
                    ind_publio=row[37],
                    diffcom=row[38],
                    amintret=row[39],
                    natetab=row[40],
                    libnatetab=row[41],
                    apet700=row[42],
                    libapet=row[43],
                    dapet=row[44],
                    tefet=row[45],
                    libtefet=row[46],
                    efetcent=row[47],
                    defet=row[48],
                    origine=row[49],
                    dcret=row[50],
                    ddebact=row[51],
                    activnat=row[52],
                    lieuact=row[53],
                    actisurf=row[54],
                    saisonat=row[55],
                    modet=row[56],
                    prodet=row[57],
                    prodpart=row[58],
                    auxilt=row[59],
                    nomen_long=row[60],
                    sigle=row[61],
                    nom=row[62],
                    prenom=row[63],
                    civilite=row[64],
                    rna=row[65],
                    nicsiege=row[66],
                    rpen=row[67],
                    depcomen=row[68],
                    adr_mail=row[69],
                    nj=row[70],
                    libnj=row[71],
                    apen700=row[72],
                    libapen=row[73],
                    dapen=row[74],
                    aprm=row[75],
                    ess=row[76],
                    dateess=row[77],
                    tefen=row[78],
                    libtefen=row[79],
                    efencent=row[80],
                    defen=row[81],
                    categorie=row[82],
                    dcren=row[83],
                    amintren=row[84],
                    monoact=row[85],
                    moden=row[86],
                    proden=row[87],
                    essaann=row[88],
                    tca=row[89],
                    esaapen=row[90],
                    esasec1n=row[91],
                    esasec2n=row[92],
                    esasec3n=row[93],
                    esasec4n=row[94],
                    vmaj=row[95],
                    vmaj1=row[96],
                    vmaj2=row[97],
                    vmaj3=row[98],
                    datemaj=row[99],
                ).save()

            elif BaseSiren.objects.filter(siren=row[0]).count() == 1:
                base_siren = BaseSiren.objects.get(siren=row[0])

                base_siren.siren = row[0]
                base_siren.nic = row[1]
                base_siren.l1_normalisee = row[2]
                base_siren.l2_normalisee = row[3]
                base_siren.l3_normalisee = row[4]
                base_siren.l4_normalisee = row[5]
                base_siren.l5_normalisee = row[6]
                base_siren.l6_normalisee = row[7]
                base_siren.l7_normalisee = row[8]
                base_siren.l1_declaree = row[9]
                base_siren.l2_declaree = row[10]
                base_siren.l3_declaree = row[11]
                base_siren.l4_declaree = row[12]
                base_siren.l5_declaree = row[13]
                base_siren.l6_declaree = row[14]
                base_siren.l7_declaree = row[15]
                base_siren.numvoie = row[16]
                base_siren.indrep = row[17]
                base_siren.typvoie = row[18]
                base_siren.libvoie = row[19]
                base_siren.codpos = row[20]
                base_siren.cedex = row[21]
                base_siren.rpet = row[22]
                base_siren.libreg = row[23]
                base_siren.depet = row[24]
                base_siren.arronet = row[25]
                base_siren.ctonet = row[26]
                base_siren.comet = row[27]
                base_siren.libcom = row[28]
                base_siren.du = row[29]
                base_siren.tu = row[30]
                base_siren.uu = row[31]
                base_siren.epci = row[32]
                base_siren.tcd = row[33]
                base_siren.zemet = row[34]
                base_siren.siege = row[35]
                base_siren.enseigne = row[36]
                base_siren.ind_publio = row[37]
                base_siren.diffcom = row[38]
                base_siren.amintret = row[39]
                base_siren.natetab = row[40]
                base_siren.libnatetab = row[41]
                base_siren.apet700 = row[42]
                base_siren.libapet = row[43]
                base_siren.dapet = row[44]
                base_siren.tefet = row[45]
                base_siren.libtefet = row[46]
                base_siren.efetcent = row[47]
                base_siren.defet = row[48]
                base_siren.origine = row[49]
                base_siren.dcret = row[50]
                base_siren.ddebact = row[51]
                base_siren.activnat = row[52]
                base_siren.lieuact = row[53]
                base_siren.actisurf = row[54]
                base_siren.saisonat = row[55]
                base_siren.modet = row[56]
                base_siren.prodet = row[57]
                base_siren.prodpart = row[58]
                base_siren.auxilt = row[59]
                base_siren.nomen_long = row[60]
                base_siren.sigle = row[61]
                base_siren.nom = row[62]
                base_siren.prenom = row[63]
                base_siren.civilite = row[64]
                base_siren.rna = row[65]
                base_siren.nicsiege = row[66]
                base_siren.rpen = row[67]
                base_siren.depcomen = row[68]
                base_siren.adr_mail = row[69]
                base_siren.nj = row[70]
                base_siren.libnj = row[71]
                base_siren.apen700 = row[72]
                base_siren.libapen = row[73]
                base_siren.dapen = row[74]
                base_siren.aprm = row[75]
                base_siren.ess = row[76]
                base_siren.dateess = row[77]
                base_siren.tefen = row[78]
                base_siren.libtefen = row[79]
                base_siren.efencent = row[80]
                base_siren.defen = row[81]
                base_siren.categorie = row[82]
                base_siren.dcren = row[83]
                base_siren.amintren = row[84]
                base_siren.monoact = row[85]
                base_siren.moden = row[86]
                base_siren.proden = row[87]
                base_siren.essaann = row[88]
                base_siren.tca = row[89]
                base_siren.esaapen = row[90]
                base_siren.esasec1n = row[91]
                base_siren.esasec2n = row[92]
                base_siren.esasec3n = row[93]
                base_siren.esasec4n = row[94]
                base_siren.vmaj = row[95]
                base_siren.vmaj1 = row[96]
                base_siren.vmaj2 = row[97]
                base_siren.vmaj3 = row[98]
                base_siren.datemaj = row[99]

                base_siren.save()
    return


def executor_import_stock_file():
    with open(str("/Users/nicolaschanton/Downloads/sirc-17804_9075_61173_201808_L_M_20180901_015350280.csv"), "rt",
              encoding='latin-1') as csvfile:
        filereader = csv.reader(csvfile, delimiter=';', quotechar='"')

        filereader_list = list(filereader)

        print(filereader_list)

        with ThreadPoolExecutor(max_workers=25) as executor:
            executor.map(import_stock_file, filereader_list)
    return
