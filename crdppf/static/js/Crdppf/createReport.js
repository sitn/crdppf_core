Ext.namespace('Crdppf');

Crdppf.Report= {

    interval: null,

    currentStatus: null,

    pdfMask: null,

    create: function(url, pdfMask) {

        this.pdfMask = pdfMask;

        if (Crdppf.pdfRenderEngine == 'crdppf_mfp'){
          Ext.Ajax.request({
              url: url,
              success: function(response) {
                    var result = Ext.decode(response.responseText);
                    this.currentStatus = 0;
                    this.printManager(result.ref, false);

              },
              method: 'GET',
              timeout: 80000,
              failure: function () {
                  Ext.Msg.alert(Crdppf.labels.serverErrorMessage);
                  pdfMask.hide();
              },
              scope: this
          });
        } else {
          window.location.href = url;
          pdfMask.hide();
          Ext.getCmp('pdfExtractWindow').hide();
        }
    },

    printManager: function(ref, status) {

        var me = this;

        if (!this.interval) {
            this.interval = setInterval(function() {
                me.getStatus(ref, status);
            }, Math.max(500, this.currentStatus * 0.6));
        }
        if (status === true) {
            clearInterval(this.interval);
            this.getReport(ref);
        }
    },

    getStatus: function(ref) {

        Ext.Ajax.request({
            url: Crdppf.printReportStatusUrl+ref+'.json',
            method: 'GET',
            success: function(response) {
                this.printManager(ref, Ext.decode(response.responseText).done);
            },
            failure: function(response) {
                Ext.Msg.alert(Crdppf.labels.serverErrorMessage);
                clearInterval(this.interval);
                this.pdfMask.hide();
                this.interval = null;
                this.currentStatus = null;
                this.pdfMask = null;
                this.interval = null;
                return;
            },
            params: this.baseParams,
            scope: this
        });
    },

    getReport: function(ref) {
        if (Crdppf.pdfRenderEngine == 'crdppf_mfp'){
          var pdfurl = [
              Crdppf.printReportGetUrl,
              ref
          ].join('');
        } else {
          var pdfurl = ref;
        }
        var button = Ext.getCmp('pdfDisplayButton');
        button.setHandler(function() {window.open(pdfurl);});
        Ext.getCmp('pdfDisplayPanel').show();
        Ext.getCmp('pdfChoicePanel').hide();
        this.pdfMask.hide();
        this.interval = null;
        this.currentStatus = null;
        this.pdfMask = null;
    }

};
