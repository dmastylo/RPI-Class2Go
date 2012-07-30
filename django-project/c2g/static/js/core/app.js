
(function() {

    // Datepicker
    $('[data-datetimepicker]').datetimepicker({
        ampm: true
    });

    // Exercise list drag and drop
    function updateExerciseOrder(itemIndex, order, $container) {
    var listElementId = order[itemIndex],
        $listItem = $container.find("#" + listElementId);

    $listItem
      .find("input")
      .val(itemIndex);
    }

    $("[data-sortablecontainer]")
    .sortable({
      placeholder: "ui-state-highlight",
      update: function(event, ui) {
        var $this = $(this),
            order = $this.sortable("toArray"),
            key;
          
        for (key in order) {
          updateExerciseOrder(key, order, $this);
        }

      }
    })
    .disableSelection();
    
})();