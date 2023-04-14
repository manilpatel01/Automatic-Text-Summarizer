$(() => {
  $("#text").attr("autocomplete", "off");
  $("#lines").attr("autocomplete", "off");
  $("#button").on("click", (event) => {
    // Regex to match URL
    const exp = /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/gi;
    const regex = new RegExp(exp);

    if (
      isNaN($("#lines").val()) ||
      $("#lines").val() < 1 ||
      $("#lines").val() > 15
    ) {
      alert(
        "Document can be summarised at least in 1 line and at most in 15 lines"
      );
      return false;
    }
    
    $("#loading").show();

    if($("#text").isNaN){
        $.ajax({
        data: {
          text: $("#text").val(),
          lines: parseInt($("#lines").val()),
        },
        type: "POST",
        url: "/test1",
        cache: false,
      }).done((data) => {
        $("#loading").hide();
        $("#output").html("");
        jQuery.each(data, (i, val) => {
          $("#output").append("<li>" + val + "</li>");
        });
      });
      event.preventDefault();
    }

    if ($("#text").val().match(regex)) {
      $.ajax({
        data: {
          url: $("#text").val(),
          lines: parseInt($("#lines").val()),
        },
        type: "POST",
        url: "/test",
        cache: false,
      }).done((data) => {
        $("#loading").hide();
        $("#output").html("");
        jQuery.each(data, (i, val) => {
          $("#output").append("<li>" + val + "</li>");
        });
      });
      event.preventDefault();
    } else {
      $.ajax({
        data: {
          text: $("#text").val(),
          lines: parseInt($("#lines").val()),
        },
        type: "POST",
        url: "/test1",
        cache: false,
      }).done((data) => {
        $("#loading").hide();
        $("#output").html("");
        jQuery.each(data, (i, val) => {
          $("#output").append("<li>" + val + "</li>");
        });
      });
      event.preventDefault();
    }
  });

});
