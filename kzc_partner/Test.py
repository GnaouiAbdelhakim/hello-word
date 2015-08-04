# -*- coding: utf-8 -*-

from openerp import models, fields, api



class test(models.Model):

     _name = 'kzc_partner.Test'


     x = fields.Float(String="X",default=50)
     y = fields.Float(compute='_compute_total',String="Y")



     @api.one
     @api.depends('x')
     def _compute_total(self):

         self.y=self.x*2


     @api.one
     def _execute(self):

        print "exe"
        return 200,


     def main(self):
        t=test()
        print self.x


     if  __name__ =='__main__':main()



test()