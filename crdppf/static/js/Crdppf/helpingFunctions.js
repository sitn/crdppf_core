// Global static public helping functions

Ext.namespace('Crdppf');

// Generate UUID
Crdppf.s4 = function () {
  return Math.floor((1 + Math.random()) * 0x10000)
             .toString(16)
             .substring(1);
};

// Generate UUID V4
Crdppf.uuid =  function () {
  return Crdppf.s4() + Crdppf.s4() + '-' + Crdppf.s4() + '-' + Crdppf.s4() + '-' +
         Crdppf.s4() + '-' + Crdppf.s4() + Crdppf.s4() + Crdppf.s4();
};

// Check if and element belongs to a list
Crdppf.contains = function (element,list){
        for (var item in list) {
            if (list[item] == element){
                return true;
            }
        }
    return false;
};
