
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (c) 2007 Ferran Pegueroles <ferran@pegueroles.com>
#    Copyright (c) 2009 Albert Cervera i Areny <albert@nan-tic.com>
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Fiche Partenaire",
    'version': '1.0',
    'category': '',
    "description": """
    --Versions--\n
    --> v1 : Dev initial. \n
    --\n
    L'objectif de se module est d'enrichir la fiche partenaire (client & fournisseur) standard d'OpenERP, avec un certain nombre d'informations d'ordre financier et commercial.
    """,
    'author': 'Kazacube',
    'website': 'http://www.kazacube.com',
    "depends" : ['base','sale_stock','stock','account','purchase'],
    "init_xml" : [],
    "update_xml" : [
                    'partner_view.xml',
                    'report/partner_reportQ.xml',
                    'Dec_qweb_report.xml',
                    ],
    "css": ['static/src/css/style.css'],
    "demo_xml" : [],
    "data" : [],
    "active": False,
    "installable": True,
}
