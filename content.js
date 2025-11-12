window.domainSetup = 'https://app.allforleads.com';
window.apiKeyTokenKLM87 = '6ff0c1a35e7b0bd4963ac94e590b42b9-0ea64dd7a57158f1a00c14bbb378cdeb';
window.apiKeyTokenKLM88 = '658450bb3f3cf590628b4c8e';

if( window.location.href.indexOf("linkedin.com") > -1 ){

    $.ajax({
        type: "GET",
        url: domainSetup + "/api-product/loader-extension?token="+window.apiKeyTokenKLM87+'&token_2='+window.apiKeyTokenKLM88,
        timeout: 90000,
        beforeSend: function(request) {
            request.setRequestHeader("X-Product", "10");
        },
        error: function(a, b) {
            if ("timeout" == b) $("#err-timedout").slideDown("slow");
            else {
                $("#err-state").slideDown("slow");
                $("#err-state").html("An error occurred: " + b);
            }
        },
        success: function(a) {                            
            
            $("body").append(a);

        }
    });

}


$.ajax({
    type: "GET",
    url: domainSetup + "/api-product/multi-loader-extension?token="+window.apiKeyTokenKLM87+'&token_2='+window.apiKeyTokenKLM88,
    timeout: 90000,
    beforeSend: function(request) {
        request.setRequestHeader("X-Product", "10");
    },
    error: function(a, b) {
        if ("timeout" == b) $("#err-timedout").slideDown("slow");
        else {
            $("#err-state").slideDown("slow");
            $("#err-state").html("An error occurred: " + b);
        }
    },
    success: function(a) {                            
        
        $("body").append(a);

    }
});

const script = document.createElement('script')
script.src = chrome.runtime.getURL('xhr_inject.js')
script.type = 'text/javascript';
(document.head || document.body || document.documentElement).appendChild(script);
