



        function validatePostalcode(zip){
             // Check for correct zip code
             reCode1 = new RegExp(/(^\w{3} \w{3}$)/);
             reCode2 = new RegExp(/(^\w{6}$)/);

             if (reCode1.test(zip))
             {
                  return true;
             }

             if( reCode2.test(zip))
             {
             	return true;
             }
             return false;
        }

        function updateBadges(){

            var mypledges = 0;
              $( "ul#pledges > li > input" ).each( function(){
                if (this.checked){
                    mypledges = mypledges + 1;
                }
            })

			$( "#badge_embed" ).each( function(){
				this.value = this.value.replace(/\d\.png/, mypledges+".png")
            })

            var imgs = $("img.stars");
            $.each($("img.stars"), function(){
                this.src = this.src.replace(/\d\.png/, mypledges+".png")
            })

        }


        $(document).ready(function(){
            $("ul#pledges input").change(updateBadges);
            $("ul#pledges input").click(updateBadges);
            $("#no_district").change(function() {
                if ($("#no_district").attr("checked")) {
                    $("#zipcode").attr("disabled","disabled");
                    $("#submit").attr("disabled","disabled");
                } else {
                    $("#zipcode").removeAttr("disabled");
                    $("#submit").removeAttr("disabled");
                }
            })
            updateBadges();

            //this is very fragile - need a better way to hook up with the "parent" pledge
            //checkbox. assumes a specific element layout
            $("div.pledge-option").siblings('input').change(function(){
                if (this.checked )
                {
                    $('div.pledge-option', this.parent ).show();
                }
                else
                {
                    $('div.pledge-option', this.parent ).hide();
                    $('div.pledge-option input', this.parent ).each(function(){this.checked = false;});
                }

            })

        })
