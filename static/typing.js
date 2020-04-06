
$(document).ready(function() {
    var options = {
      stringsElement:"#typed-strings",
      //strings: ['⠀Vent Out. <span class="text-muted">Without Judgement.</span>', '⠀Get Advice. <span class="text-muted">From Real Therapists.</span>','⠀Book Appointments. <span class="text-muted">If Needed.</span>'],
      typeSpeed: 50,
      backSpeed: 50,
      smartBackspace: true,
      loop: true,
      loopCount: Infinity,
      showCursor: false
    };

    var typed = new Typed('#typed', options);
});
