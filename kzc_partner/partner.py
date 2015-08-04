
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

from openerp import api
from openerp.osv import osv,fields
from openerp.tools.translate import _
from datetime import datetime

class res_partner(osv.osv):
    _inherit = 'res.partner' 



    # function 1

    def _get_customer_invoice(self,cr,uid,ids,fields, arg=None,context=None):
        result = {}
        if not ids: return result
        invoice_obj = self.pool.get('account.invoice')
        for id in ids:
           result.setdefault(id, [])
        invoice_ids = invoice_obj.search(cr,uid,[('partner_id','=',ids[0]),('type','in',('out_invoice','out_refund'))],limit=10, order= 'date_invoice desc')
        if invoice_ids :
            for i in range(len(invoice_ids)):
                result[id].append(invoice_ids[i])


        return result



    # function 1:1 browse

    def _get_customer_invoice_r(self,cr,uid,ids,fields, arg=None,context=None):

        invoice_obj = self.pool.get('account.invoice')

        invoices = invoice_obj.search(cr,uid,[('partner_id','=',ids[0]),('type','in',('out_invoice','out_refund'))],limit=10, order= 'date_invoice desc')

        result = invoice_obj.browse(cr,uid,invoices)

        return result


    # function 2

    def _get_supplier_invoice(self,cr,uid,ids,fields, arg=None,context=None):
        result = {}
        if not ids: return result
        invoice_obj = self.pool.get('account.invoice')
        for id in ids:
           result.setdefault(id, [])
        invoice_ids = invoice_obj.search(cr,uid,[('partner_id','=',ids[0]),('type','in',('in_invoice','in_refund'))],limit=10, order= 'date_invoice desc')
        if invoice_ids :
            for i in range(len(invoice_ids)):
                result[id].append(invoice_ids[i])


        return result

    # function 3 fonction de test

    # l'objectif de ce test est de supporté les différente devis lors de la facturation au près d'un client.

    def _get_current_invoice_turnover(self, cr, uid, ids, field_name, arg,context=None):


        res = {}
        period_ids = []
        turnover = 0

        if not ids: return res
        for id in ids:
           res.setdefault(id, [])
        current_year = datetime.now().year
        cr.execute('''select id from account_period where special = False and fiscalyear_id in (select id from account_fiscalyear where name::integer = %s)'''%current_year)
        result = cr.fetchall()

        for period_id in range(len(result)):
            period_ids.append(result[period_id][0])

        # chargé le modèle de la classe account.invoice
        invoice_obj = self.pool.get('account.invoice')
        # cherché les identifiants des objets (facture) en ce basant sur un ensemble de critères
        invoice_ids = invoice_obj.search(cr,uid,[('partner_id','=',ids[0]),('type','in',('out_invoice','out_refund')),('period_id','in',period_ids),('state','in',('open','paid'))])
        if invoice_ids:
            for invoice in invoice_obj.browse(cr,uid,invoice_ids):

                if invoice.type == 'out_invoice':
                 #   turnover += invoice.amount_total
                   turnover += self._calc_currency_mad_inv(cr, uid,ids, invoice)



                if invoice.type == 'out_refund':
                    turnover -= self._calc_currency_mad_inv(cr, uid,ids, invoice)
        #print "turnover =============",turnover
        #res[id]=turnover
        #print ids[0]
        #res[id]=self._add_amount_currency_symbol(cr, uid,ids[0],turnover)
        res[id]=turnover
        # traitement faissant l'affichage des factures avec leurs devis :
        """
        t=0
        for obj in invoice_obj.browse(cr,uid,invoice_ids):
            print "facture montant : %f , monnais_id : %s"%(obj.amount_total,obj.currency_id.id)
            t+=obj.amount_total

        print "Total is : %f"%(t)
        """
        #print "res =============",res

        cr.execute('''update res_partner set current_invoice_turnover=%.2f where id=%d ;'''%(turnover,id))

        return res



    def _get_current_invoice_turnover_v(self, cr, uid, ids, field_name, arg,context=None):

       res={}
       res[ids[0]]= self._add_amount_currency_symbol(cr, uid,ids[0],self._get_current_invoice_turnover(cr,uid,ids,field_name,arg,context)[ids[0]])
       return res

    # function 4
    
    def _get_previous_invoice_turnover(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        period_ids = []
        turnover = 0
        if not ids: return res
        for id in ids:
           res.setdefault(id, [])
        previous_year = datetime.now().year - 1
        cr.execute('''select id from account_period where special = False and fiscalyear_id in (select id from account_fiscalyear where name::integer = %s)'''%previous_year)
        result = cr.fetchall()
        if len(result) >= 1:
            for period_id in range(len(result)):
                period_ids.append(result[period_id][0])
            
            invoice_obj = self.pool.get('account.invoice')
            invoice_ids = invoice_obj.search(cr,uid,[('partner_id','=',ids[0]),('type','in',('out_invoice','out_refund')),('period_id','in',period_ids),('state','in',('open','paid'))])
            if invoice_ids:
                for invoice in invoice_obj.browse(cr,uid,invoice_ids):
                    if invoice.type == 'out_invoice':
                        turnover += self._calc_currency_mad_inv(cr, uid,ids, invoice)
                    if invoice.type == 'out_refund':
                        turnover -= self._calc_currency_mad_inv(cr, uid,ids, invoice)

            res[id]=turnover

            cr.execute('''update res_partner set previous_invoice_turnover=%.2f where id=%d ;'''%(res[id],id))

            return res

        else:
            res[id]=0

            cr.execute('''update res_partner set previous_invoice_turnover=%.2f where id=%d ;'''%(res[id],id))

            return res


    def _get_previous_invoice_turnover_v(self, cr, uid, ids, field_name, arg,context=None):

       res={}
       res[ids[0]]= self._add_amount_currency_symbol(cr, uid,ids[0],self._get_previous_invoice_turnover(cr,uid,ids,field_name,arg,context)[ids[0]])
       return res

    # function 5

    def _get_current_order_turnover(self, cr, uid, ids, field_name, arg, context=None):


        res = {}
        period_ids = []
        turnover = 0
        if not ids: return res
        for id in ids:
           res.setdefault(id, [])
        current_year = str(datetime.now().year)
        fiscalyear_obj=self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(cr,uid,[('name','=',current_year)])
        fiscalyear = fiscalyear_obj.browse(cr,uid,fiscalyear_ids[0])
        
        order_obj = self.pool.get('sale.order')
        order_ids_ids = order_obj.search(cr,uid,[('partner_id','=',ids[0]),('date_confirm','>=',fiscalyear.date_start),('date_confirm','<=',fiscalyear.date_stop),('state','not in',('draft','cancel'))])
        if order_ids_ids:

            for order in order_obj.browse(cr,uid,order_ids_ids):
                turnover += self._calc_currency_mad_ord(cr, uid,ids, order)
        res[id]=turnover

        cr.execute('''update res_partner set current_order_turnover=%.2f where id=%d ;'''%(res[id],id))

        return res

    def _get_current_order_turnover_v(self, cr, uid, ids, field_name, arg,context=None):

       res={}
       res[ids[0]]= self._add_amount_currency_symbol(cr, uid,ids[0],self._get_current_order_turnover(cr,uid,ids,field_name,arg,context)[ids[0]])
       return res


    # function 6

    def _get_previous_order_turnover(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        period_ids = []
        turnover = 0
        if not ids: return res
        for id in ids:
           res.setdefault(id, [])
        current_year = str(datetime.now().year - 1)
        fiscalyear_obj=self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(cr,uid,[('name','=',current_year)])
        if fiscalyear_ids:
            fiscalyear = fiscalyear_obj.browse(cr,uid,fiscalyear_ids[0])
            order_obj = self.pool.get('sale.order')
            order_ids_ids = order_obj.search(cr,uid,[('partner_id','=',ids[0]),('date_confirm','>=',fiscalyear.date_start),('date_confirm','<=',fiscalyear.date_stop),('state','not in',('draft','cancel'))])
            if order_ids_ids:

                for order in order_obj.browse(cr,uid,order_ids_ids):
                    turnover +=  self._calc_currency_mad_ord(cr, uid,ids, order)
            res[id]=turnover

            cr.execute('''update res_partner set previous_order_turnover=%.2f where id=%d ;'''%(res[id],id))

            return res
        else :
            res[id]=0

            cr.execute('''update res_partner set previous_order_turnover=%.2f where id=%d ;'''%(res[id],id))

            return res

    def _get_previous_order_turnover_v(self, cr, uid, ids, field_name, arg,context=None):

       res={}
       res[ids[0]]= self._add_amount_currency_symbol(cr, uid,ids[0],self._get_previous_order_turnover(cr,uid,ids,field_name,arg,context)[ids[0]])
       return res


    # function 7

    def _get_current_invoice_purchase(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        period_ids = []
        turnover = 0
        if not ids: return res
        for id in ids:
           res.setdefault(id, [])
        current_year = datetime.now().year
        cr.execute('''select id from account_period where special = False and fiscalyear_id in (select id from account_fiscalyear where name::integer = %s)'''%current_year)
        result = cr.fetchall()
        for period_id in range(len(result)):
            period_ids.append(result[period_id][0])
        
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(cr,uid,[('partner_id','=',ids[0]),('type','in',('in_invoice','in_refund')),('period_id','in',period_ids),('state','in',('open','paid'))])
        if invoice_ids:
            for invoice in invoice_obj.browse(cr,uid,invoice_ids):
                if invoice.type == 'in_invoice':
                    turnover += self._calc_currency_mad_inv(cr, uid,ids, invoice)
                if invoice.type == 'in_refund':
                    turnover -= self._calc_currency_mad_inv(cr, uid,ids, invoice)
        res[id]=turnover

        cr.execute('''update res_partner set current_invoice_purchase=%.2f where id=%d ;'''%(res[id],id))

        return res


    def _get_current_invoice_purchase_v(self, cr, uid, ids, field_name, arg,context=None):

       res={}
       res[ids[0]]= self._add_amount_currency_symbol(cr, uid,ids[0],self._get_current_invoice_purchase(cr,uid,ids,field_name,arg,context)[ids[0]])
       return res

    # function 8
    
    def _get_previous_invoice_purchase(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        period_ids = []
        turnover = 0
        if not ids: return res
        for id in ids:
           res.setdefault(id, [])
        current_year = datetime.now().year - 1
        cr.execute('''select id from account_period where special = False and fiscalyear_id in (select id from account_fiscalyear where name::integer = %s)'''%current_year)
        result = cr.fetchall()
        if len(result) >= 1:
            for period_id in range(len(result)):
                period_ids.append(result[period_id][0])
            
            invoice_obj = self.pool.get('account.invoice')
            invoice_ids = invoice_obj.search(cr,uid,[('partner_id','=',ids[0]),('type','in',('in_invoice','in_refund')),('period_id','in',period_ids),('state','in',('open','paid'))])
            if invoice_ids:
                for invoice in invoice_obj.browse(cr,uid,invoice_ids):
                    if invoice.type == 'in_invoice':
                        turnover += self._calc_currency_mad_inv(cr, uid,ids, invoice)
                    if invoice.type == 'in_refund':
                        turnover -= self._calc_currency_mad_inv(cr, uid,ids, invoice)
            res[id]=turnover

            cr.execute('''update res_partner set previous_invoice_purchase=%.2f where id=%d ;'''%(res[id],id))

            return res
        else :
            res[id]=0

            cr.execute('''update res_partner set previous_invoice_purchase=%.2f where id=%d ;'''%(res[id],id))

            return res

    def _get_previous_invoice_purchase_v(self, cr, uid, ids, field_name, arg,context=None):

       res={}
       res[ids[0]]= self._add_amount_currency_symbol(cr, uid,ids[0],self._get_previous_invoice_purchase(cr,uid,ids,field_name,arg,context)[ids[0]])
       return res


    # function 9

    def _get_current_order_purchase(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        period_ids = []
        turnover = 0
        if not ids: return res
        for id in ids:
           res.setdefault(id, [])
        current_year = str(datetime.now().year)
        fiscalyear_obj=self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(cr,uid,[('name','=',current_year)])
        fiscalyear = fiscalyear_obj.browse(cr,uid,fiscalyear_ids[0])
        
        order_obj = self.pool.get('purchase.order')
        order_ids_ids = order_obj.search(cr,uid,[('partner_id','=',ids[0]),('date_approve','>=',fiscalyear.date_start),('date_approve','<=',fiscalyear.date_stop),('state','not in',('draft','cancel'))])
        if order_ids_ids:
            for order in order_obj.browse(cr,uid,order_ids_ids):
                turnover += self._calc_currency_mad_ord(cr, uid,ids, order)
        res[id]=turnover

        cr.execute('''update res_partner set current_order_purchase=%.2f where id=%d ;'''%(res[id],id))

        return res

    def _get_current_order_purchase_v(self, cr, uid, ids, field_name, arg,context=None):

       res={}
       res[ids[0]]= self._add_amount_currency_symbol(cr, uid,ids[0],self._get_current_order_purchase(cr,uid,ids,field_name,arg,context)[ids[0]])
       return res

    # function 10
    
    def _get_previous_order_purchase(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        period_ids = []
        turnover = 0
        if not ids: return res
        for id in ids:
           res.setdefault(id, [])
        current_year = str(datetime.now().year - 1)
        fiscalyear_obj=self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(cr,uid,[('name','=',current_year)])
        if fiscalyear_ids:
            fiscalyear = fiscalyear_obj.browse(cr,uid,fiscalyear_ids[0])
            order_obj = self.pool.get('purchase.order')
            order_ids_ids = order_obj.search(cr,uid,[('partner_id','=',ids[0]),('date_approve','>=',fiscalyear.date_start),('date_approve','<=',fiscalyear.date_stop),('state','not in',('draft','cancel'))])
            if order_ids_ids:
                for order in order_obj.browse(cr,uid,order_ids_ids):
                    turnover += self._calc_currency_mad_ord(cr, uid,ids, order)
            res[id]=turnover

            cr.execute('''update res_partner set previous_order_purchase=%.2f where id=%d ;'''%(res[id],id))

            return res
        else:
            res[id]=0

            cr.execute('''update res_partner set previous_order_purchase=%.2f where id=%d ;'''%(res[id],id))

            return res


    def _get_previous_order_purchase_v(self, cr, uid, ids, field_name, arg,context=None):

       res={}
       res[ids[0]]= self._add_amount_currency_symbol(cr, uid,ids[0],self._get_previous_order_purchase(cr,uid,ids,field_name,arg,context)[ids[0]])
       return res


        # function 11
    
    def _get_sale_order(self,cr,uid,ids,fields, arg=None,context=None):


        result = {}
        if not ids: return result
        order_obj = self.pool.get('sale.order')
        for id in ids:
           result.setdefault(id, [])
        order_ids = order_obj.search(cr,uid,[('partner_id','=',ids[0])],limit=10, order= 'date_order desc')
        if order_ids :
            for i in range(len(order_ids)):

                result[id].append(order_ids[i])

        return result

    # function 12
    
    def _get_products_move(self,cr,uid,ids,fields, arg=None,context=None):
        result = {}
        if not ids: return result
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        for id in ids:
           result.setdefault(id, [])
        pick_ids = pick_obj.search(cr,uid,[('partner_id','=',ids[0]),('move_type','=','direct'),('name','not ilike','%retour%')])

        move_ids = move_obj.search(cr,uid,[('picking_id','in',pick_ids)],limit=10, order= 'date desc')

        if move_ids :
            for i in range(len(move_ids)):
                result[id].append(move_ids[i])
        return result

    # function 13

    def _get_top_saled_products(self,cr,uid,ids,fields, arg=None,context=None):
        result = {}
        previous_fiscalyear = False
        previous_pick_ids = []
        if not ids: return result
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        sale_prod = self.pool.get('sale.products')
        current_year = str(datetime.now().year)
        previous_year = str(datetime.now().year - 1)
        product_ids = []
        fiscalyear_obj=self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(cr,uid,[('name','=',current_year)])
        fiscalyear = fiscalyear_obj.browse(cr,uid,fiscalyear_ids[0])
        previous_fiscalyear_ids = fiscalyear_obj.search(cr,uid,[('name','=',previous_year)])
        if previous_fiscalyear_ids :
            previous_fiscalyear = fiscalyear_obj.browse(cr,uid,previous_fiscalyear_ids[0])
        for id in ids:
           result.setdefault(id, [])
        pick_ids = pick_obj.search(cr,uid,[('partner_id','=',ids[0]),('move_type','=','direct'),('name','not ilike','%retour%'),('date','>=',fiscalyear.date_start),('date','<=',fiscalyear.date_stop)])
        if not pick_ids : return result
        if len(pick_ids) == 1 :
            cr.execute('''select product_id,product_uom,sum(product_qty) from stock_move where picking_id = %s group by product_id,product_uom order by sum(product_qty) desc limit 5'''%(tuple(pick_ids)))
        else :
            cr.execute('''select product_id,product_uom,sum(product_qty) from stock_move where picking_id in %s group by product_id,product_uom order by sum(product_qty) desc limit 5'''%(tuple(pick_ids),))
        res=cr.fetchall()
        if previous_fiscalyear:
            previous_pick_ids = pick_obj.search(cr,uid,[('partner_id','=',ids[0]),('move_type','=','direct'),('name','not ilike','%retour%'),('date','>=',previous_fiscalyear.date_start),('date','<=',previous_fiscalyear.date_stop)])
            res_previous = cr.fetchall()
        product_number = len(res)
        cr.execute('''DELETE FROM sale_products WHERE partner_id = %s'''%ids[0])
        for r in range(len(res)):
            prev_qty=0
            if previous_pick_ids:
                cr.execute('''select product_id,product_uom,sum(product_qty) from stock_move where picking_id in %s and product_id = %s and product_uom = %s group by product_id,product_uom order by sum(product_qty) desc limit 5'''%(tuple(previous_pick_ids),res[r][0],res[r][1],),)
                prev_res=cr.fetchall()
                if prev_res:
                    prev_qty=prev_res[0][2]
            top_id = sale_prod.create(cr,uid,{'partner_id':ids[0],
                                              'product_id':res[r][0],
                                              'product_uom':res[r][1],
                                              'current_qty':res[r][2],
                                              'previous_qty':prev_qty,
                                                  })

            result[id].append(top_id)
        if product_number < 5 and previous_pick_ids :
            i=0
            cr.execute('''select product_id,product_uom,sum(product_qty) from stock_move where picking_id in %s group by product_id,product_uom order by sum(product_qty) desc limit 5'''%(tuple(previous_pick_ids),))
            prev_res_suite=cr.fetchall()
            if len(prev_res_suite) >= (5-product_number):
                for r in range(5-product_number):
                    top_id = sale_prod.create(cr,uid,{'partner_id':ids[0],
                                                      'product_id':prev_res_suite[r][0],
                                                      'product_uom':prev_res_suite[r][1],
                                                      'previous_qty':prev_res_suite[r][2],
                                                      })
                    result[id].append(top_id)
            else:
                for r in range(len(prev_res_suite)):
                    top_id = sale_prod.create(cr,uid,{'partner_id':ids[0],
                                                      'product_id':prev_res_suite[r][0],
                                                      'product_uom':prev_res_suite[r][1],
                                                      'previous_qty':prev_res_suite[r][2],
                                                      })
                    result[id].append(top_id)

        return result


    # function 14

    def _get_purchase_order(self,cr,uid,ids,fields, arg=None,context=None):
        result = {}
        if not ids: return result
        order_obj = self.pool.get('purchase.order')
        for id in ids:
           result.setdefault(id, [])
        order_ids = order_obj.search(cr,uid,[('partner_id','=',ids[0])],limit=10, order= 'date_approve desc')
        if order_ids :
            for i in range(len(order_ids)):
                result[id].append(order_ids[i])
        return result

    # function 15
    
    def _get_purchase_products_move(self,cr,uid,ids,fields, arg=None,context=None):
        result = {}
        if not ids: return result
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        for id in ids:
           result.setdefault(id, [])
        pick_ids = pick_obj.search(cr,uid,[('partner_id','=',ids[0]),('move_type','=','direct'),('name','not ilike','%retour%')])
        move_ids = move_obj.search(cr,uid,[('picking_id','in',pick_ids)],limit=10, order= 'date desc')
        if move_ids :
            for i in range(len(move_ids)):
                result[id].append(move_ids[i])
        return result

    # function 16
    
    def _get_top_purchased_products(self,cr,uid,ids,fields, arg=None,context=None):
        result = {}
        previous_fiscalyear = False
        previous_pick_ids = []        
        if not ids: return result
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        purchase_prod = self.pool.get('purchase.products')
        current_year = str(datetime.now().year)
        previous_year = str(datetime.now().year - 1)
        product_ids = []
        fiscalyear_obj=self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(cr,uid,[('name','=',current_year)])
        fiscalyear = fiscalyear_obj.browse(cr,uid,fiscalyear_ids[0])
        previous_fiscalyear_ids = fiscalyear_obj.search(cr,uid,[('name','=',previous_year)])
        cr.execute('''DELETE FROM purchase_products WHERE partner_id = %s'''%ids[0])
        if previous_fiscalyear_ids :
            previous_fiscalyear = fiscalyear_obj.browse(cr,uid,previous_fiscalyear_ids[0])
        for id in ids:
           result.setdefault(id, [])
        pick_ids = pick_obj.search(cr,uid,[('partner_id','=',ids[0]),('move_type','=','direct'),('name','not ilike','%retour%'),('date','>=',fiscalyear.date_start),('date','<=',fiscalyear.date_stop)])
        if not pick_ids : return result
        if len(pick_ids) == 1 :
            cr.execute('''select product_id,product_uom,sum(product_qty) from stock_move where picking_id = %s group by product_id,product_uom order by sum(product_qty) desc limit 5'''%(tuple(pick_ids)))
        else:
            cr.execute('''select product_id,product_uom,sum(product_qty) from stock_move where picking_id in %s group by product_id,product_uom order by sum(product_qty) desc limit 5'''%(tuple(pick_ids),))

        res=cr.fetchall()
        if previous_fiscalyear :
            previous_pick_ids = pick_obj.search(cr,uid,[('partner_id','=',ids[0]),('move_type','=','direct'),('name','not ilike','%retour%'),('date','>=',previous_fiscalyear.date_start),('date','<=',previous_fiscalyear.date_stop)])
            res_previous = cr.fetchall()
        product_number = len(res)
        for r in range(len(res)):
            prev_qty=0
            if previous_pick_ids:
                cr.execute('''select product_id,product_uom,sum(product_qty) from stock_move where picking_id in %s and product_id = %s and product_uom = %s group by product_id,product_uom order by sum(product_qty) desc limit 5'''%(tuple(previous_pick_ids),res[r][0],res[r][1],),)
                prev_res=cr.fetchall()
                if prev_res:
                    prev_qty=prev_res[0][2]
            top_id = purchase_prod.create(cr,uid,{'partner_id':ids[0],
                                                  'product_id':res[r][0],
                                                  'product_uom':res[r][1],
                                                  'current_qty':res[r][2],
                                                  'previous_qty':prev_qty,
                                                  })
            
            result[id].append(top_id)
        if product_number < 5 and previous_pick_ids :
            i=0
            cr.execute('''select product_id,product_uom,sum(product_qty) from stock_move where picking_id in %s group by product_id,product_uom order by sum(product_qty) desc limit 5'''%(tuple(previous_pick_ids),))
            prev_res_suite=cr.fetchall()
            if len(prev_res_suite) >= (5-product_number):
                for r in range(5-product_number):
                    top_id = purchase_prod.create(cr,uid,{'partner_id':ids[0],
                                                          'product_id':prev_res_suite[r][0],
                                                          'product_uom':prev_res_suite[r][1],
                                                          'previous_qty':prev_res_suite[r][2],
                                                      })
                    result[id].append(top_id)
            else:
                for r in range(len(prev_res_suite)):
                    top_id = purchase_prod.create(cr,uid,{'partner_id':ids[0],
                                                          'product_id':prev_res_suite[r][0],
                                                          'product_uom':prev_res_suite[r][1],
                                                          'previous_qty':prev_res_suite[r][2],
                                                      })
                    result[id].append(top_id)
        return result


    # function 17

    def _calc_currency_mad_inv(self,cr,uid,ids,invoice):

        context={}
        tmp=0
        currency_obj = self.pool.get('res.currency')
        context.update({'date': invoice.date_due})



        tmp = currency_obj.compute(cr, uid, invoice.currency_id.id,invoice.company_id.currency_id.id ,invoice.amount_untaxed,context=context)

        return tmp

    # function 18

    def _calc_currency_mad_ord(self,cr,uid,ids,order):

        context={}
        tmp=0
        currency_obj = self.pool.get('res.currency')
        context.update({'date': order.date_order})
        tmp = currency_obj.compute(cr, uid, order.pricelist_id.currency_id.id,order.company_id.currency_id.id ,order.amount_untaxed,context=context)

        return tmp


    # function 19

    def _add_amount_currency_symbol(self, cr, uid,id_partner,amount):


         # méthode  : modéle objet


        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr,uid,[('id','=',id_partner)])
        if partner_id:
            for partner in partner_obj.browse(cr,uid,partner_id):

                symbol= partner.company_id.currency_id.symbol


        return str(amount)+" "+symbol



    
    _columns = {
            ########10 last invoice##############
            'customer_invoice_ids':fields.function(_get_customer_invoice,type='one2many',relation='account.invoice',string="Customer Invoice"),
            'supplier_invoice_ids':fields.function(_get_supplier_invoice,type='one2many',relation='account.invoice',string="Customer Invoice"),               
            #####Invoice Turnover########
            'current_invoice_turnover_v':fields.function(_get_current_invoice_turnover_v,type='text',string='Invoice Turnover'),
            'current_invoice_turnover':fields.function(_get_current_invoice_turnover,type='float',string='Invoice Turnover',store=True),
            'previous_invoice_turnover_v':fields.function(_get_previous_invoice_turnover_v,type='text', string='Invoice Turnover' ),
            'previous_invoice_turnover':fields.function(_get_previous_invoice_turnover,type='float', string='Invoice Turnover',store=True),
            #####Sale Order Turnover########
            'current_order_turnover_v':fields.function(_get_current_order_turnover_v,type='text', string='Order Turnover' ),
            'current_order_turnover':fields.function(_get_current_order_turnover,type='float', string='Order Turnover',store=True),
            'previous_order_turnover_v':fields.function(_get_previous_order_turnover_v,type='text', string='Order Turnover' ),
            'previous_order_turnover':fields.function(_get_previous_order_turnover,type='float', string='Order Turnover',store=True),
            #####Purchase Invoice######
             'current_invoice_purchase_v':fields.function(_get_current_invoice_purchase_v,type='text', string='Purchase Invoiced' ),
             'current_invoice_purchase':fields.function(_get_current_invoice_purchase,type='float', string='Purchase Invoiced',store=True),
             'previous_invoice_purchase_v':fields.function(_get_previous_invoice_purchase_v,type='text', string='Purchase Invoiced' ),
             'previous_invoice_purchase':fields.function(_get_previous_invoice_purchase,type='float', string='Purchase Invoiced',store=True),
            #####Purchase Order########
            'current_order_purchase_v':fields.function(_get_current_order_purchase_v,type='text', string='Purchase Order' ),
            'current_order_purchase':fields.function(_get_current_order_purchase,type='float', string='Purchase Order',store=True),
            'previous_order_purchase_v':fields.function(_get_previous_order_purchase_v,type='text', string='Purchase Order' ),
            'previous_order_purchase':fields.function(_get_previous_order_purchase,type='float', string='Purchase Order',store=True),
             ##sale##
             ########10 last sale order##############
             'sale_order_ids':fields.function(_get_sale_order,type='one2many',relation='sale.order',string="Sale Order"),
             ########10 last saled product##############
             'sale_stock_move_ids':fields.function(_get_products_move,type='one2many',relation='stock.move',string="Stock Move"),
             ########Top 5 saled products###################
             'top_saled_stock_move_ids':fields.function(_get_top_saled_products,type='one2many',relation='sale.products',string="Top Five"),
             ##Purchase##
             ########10 last purchase order##############
             'purchase_order_ids':fields.function(_get_purchase_order,type='one2many',relation='purchase.order',string="Purchase Order"),
             ########10 last purchased product##############
             'purchase_stock_move_ids':fields.function(_get_purchase_products_move,type='one2many',relation='stock.move',string="Stock Move"),
             ########Top 5 purchased products###################
             'top_purchased_stock_move_ids':fields.function(_get_top_purchased_products,type='one2many',relation='purchase.products',string="Top Five"),
             ######## calcule les montants en devis de la sté pour les factures  ##########
             'calculate_currency_mad_inv' : fields.function(_calc_currency_mad_inv,type='float'),
             ######## calcule les montants en devis de la sté pour les commandes ##########
            'calculate_currency_mad_ord' : fields.function(_calc_currency_mad_ord,type='float'),
             ######## symbole devis sté  ##########
            'append_currency_symbol' : fields.function(_add_amount_currency_symbol,type='text',string="Currency type"),
             ############## function report invoice ###############
            'customer_invoices':fields.function(_get_customer_invoice_r,type='one2many',relation='account.invoice',string="Customer Invoice"),
            'invoice_line': fields.one2many('account.invoice', 'partner_id', 'Invoice Lines', readonly=True, copy=True),
            'sale_order_line' : fields.one2many('sale.order', 'partner_id', 'Sale Order Lines', readonly=True, copy=True),
            'purchase_order_line' : fields.one2many('purchase.order', 'partner_id', 'Purchase Order Lines', readonly=True, copy=True),
            'top_sale_products_line' : fields.one2many('sale.products', 'partner_id', 'Top Five Sale products', readonly=True, copy=True),
            'top_purchase_products_line' : fields.one2many('purchase.products', 'partner_id', 'Top Five Purchase products', readonly=True, copy=True),
             }

res_partner()

class sale_products(osv.osv_memory):
    _name = 'sale.products'
    
    _columns = {
            'partner_id':fields.many2one('res.partner','Partner'),
            'product_id':fields.many2one('product.product','Product'),
            'product_uom':fields.many2one('product.uom','Unity'),
            'current_qty':fields.float('Current Exercise Quantity'),
            'previous_qty':fields.float('Previous Exercise Quantity'),

                        }
    
class purchase_products(osv.osv_memory):
    _name = 'purchase.products'
    
    _columns = {
            'partner_id':fields.many2one('res.partner','Partner'),
            'product_id':fields.many2one('product.product','Product'),
            'product_uom':fields.many2one('product.uom','Unity'),
            'current_qty':fields.float('Current Exercise Quantity'),
            'previous_qty':fields.float('Previous Exercise Quantity'),
            
                        }

    # class report

