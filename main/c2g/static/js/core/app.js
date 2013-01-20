(function(document, undefined) {


    var $document = $(document);

    window.c2g = window.c2g || {};

 
    c2g.installLeftNavChevron = function () {
         $('.nav-list.collapse').on("hidden shown", function(e){
                                $(this).prev().toggleClass("expanded", (e.type === "shown"))
                                });

    };
 
    c2g.createModal = function(options) {
      var opts = options || {}, // confirmText, hideCancel, body, title
        $modal,
        content = '<div class="modal hide fade">' +
          '<div class="modal-header">' + 
            '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
            '<h3>' + (opts.title ? opts.title : "&nbsp;") + '</h3>' +
          '</div>';

      content += '<div class="modal-body">' +
        '<p>' + (opts.body ? opts.body : "&nbsp;") + '</p>' +
      '</div>';

      content += '<div class="modal-footer">' +
        (opts.hideCancel ? '' : '<a href="#" data-dismiss="modal" class="btn">Cancel</a>') +
        '<a href="#" data-confirm-button class="btn btn-primary">' + (opts.confirmText ? opts.confirmText : "Save changes") + '</a>' +
      '</div>';

      content += '</div>';

      $modal = $(content);

      if (opts.confirmCallback) {
        $modal.find("[data-confirm-button]").on("click", function(e){
          opts.confirmCallback();
          $modal.modal('hide');
          e.preventDefault();
        });
      }


      $modal.modal();

      return $modal;
    };

    c2g.deleteProblemSet = function (id) {

      c2g.createModal({
        title: "Heads up!",
        // TODO cleanup, make "body" text not dependent on DOM lookups
        body: "Are you sure you want to delete this problem set '" + $("#problemset_"+id+"_title").html() + "'?", 
        // hideCancel: true,
        confirmText: "Delete Problem Set",
        confirmCallback: function() {
          // TODO could probably use some cleanup
          $("#delete_problem_set_id").val(id);
          document.forms.delete_problem_set_form.submit();
        }
      });

    };

    c2g.deleteExercise = function (id, title, problemSetTaken) {
      var body = "";

      if (problemSetTaken === "True") { // TODO this should probably come back as a boolean instead
        body = "WARNING: Students have already begun taking this problem set. Deleting an exercise can ruin the integrity of the results. Are you sure you want to delete " + title + "?";
      } else {
        body = "Are you sure you want to delete " + title + "?";
      }

      c2g.createModal({
        title: "Heads up!",
        body: body,
        // hideCancel: true,
        confirmText: "Delete Exercise",
        confirmCallback: function() {
          // TODO could probably use some cleanup
          $("#delete_exercise_id").val(id);
          document.forms.delete_exercise_form.submit();
        }
      });

    };

    c2g.toggleChevron = function (iconElemID) {
 
        if ($("#"+iconElemID).hasClass('icon-chevron-right')) {
            $("#"+iconElemID).removeClass('icon-chevron-right');
            $("#"+iconElemID).addClass('icon-chevron-down');
        }
        else if ($("#"+iconElemID).hasClass('icon-chevron-down')) {
            $("#"+iconElemID).removeClass('icon-chevron-down');
            $("#"+iconElemID).addClass('icon-chevron-right');
        }
    };


    // live events
    $document.on("click", "[data-delete-exercise]", function(e) {
      var $this = $(e.currentTarget),
        data = $this.data("exercise");

      e.preventDefault();

      c2g.deleteExercise(data.id, data.title, data.problemSetTaken);

    });

    $document.on("click", "[data-delete-problemset]", function(e) {
      var $this = $(e.currentTarget),
        data = $this.data("problemset");

      e.preventDefault();

      c2g.deleteProblemSet(data.id);

    });


    // Datepicker
    $('[data-datetimepicker]').datetimepicker({
        ampm: false
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

    // Tooltip config
    $("[data-c2g-tooltip]").tooltip();

    // Toggler
    $("[data-toggler-target]").change(function(e){
      var $this = $(this),
        isChecked = $this.is(':checked'),
        $target = $($this.data("toggler-target"));

      if (isChecked) {
        $target.show("fast");
      } else {
        $target.hide("fast");
      }
    });


})(document);