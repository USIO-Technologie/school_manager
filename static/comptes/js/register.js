console.log("✅ Script register.js chargé");

$(document).ready(function () {
    let step = "register";
    let password = "";
    const $form = $("form.my-4");

    const getLoginUrl = () => window.loginUrl || document.getElementById('login-url').value;

    $form.on("submit", function (e) {
        e.preventDefault();

        const email = $("#username").val();
        const name = $("#name").val();
        const pass1 = $("#userpassword").val();
        const pass2 = $("#Confirmpassword").val();
        const otp = $("#otp").val();
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        if (step === "register") {
            if (!email || !name || !pass1 || !pass2) {
                $form.prepend('<div class="alert alert-danger">Veuillez remplir tous les champs.</div>');
                return;
            }
            if (pass1 !== pass2) {
                $form.prepend('<div class="alert alert-danger">Les mots de passe ne correspondent pas.</div>');
                return;
            }

            password = pass1;

            $.post("/register/", {
                csrfmiddlewaretoken: csrfToken,
                step: "register",
                username: email,
                name: name,
                password: password
            }, function (data) {
                if (data.status === "otp_sent") {
                    $(".input-field-group").hide();
                    $("#otp-section").show();
                    $("#resend-otp-container").show();
                    $("#register-btn").text("Valider OTP");
                    step = "verify";
                }
            });
        }

        else if (step === "verify") {
            $.post("/register/", {
                csrfmiddlewaretoken: csrfToken,
                step: "verify",
                username: email,
                otp: otp,
                name: name,
                password: password
            }, function (data) {
                if (data.status === "verified") {
                    Swal.fire({
                        title: "Succès",
                        text: "Compte créé avec succès !",
                        icon: "success",
                    }).then(() => {
                        window.location.href = getLoginUrl();
                    });
                } else if (data.status === "expired") {
                    $form.prepend('<div class="alert alert-danger">Le code OTP a expiré.</div>');
                    location.reload();
                } else if (data.status === "blocked") {
                    $form.prepend('<div class="alert alert-danger">Trop de tentatives incorrectes.</div>');
                    location.reload();
                } else {
                    $form.prepend('<div class="alert alert-danger">Code OTP incorrect.</div>');
                }
            });
        }
    });

    $("#resend-otp-link").click(function (e) {
        e.preventDefault();

        const email = $("#username").val();
        const name = $("#name").val();
        const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

        if (!email) {
            alert("Email introuvable.");
            return;
        }

        $.post("/register/", {
            csrfmiddlewaretoken: csrfToken,
            step: "resend",
            username: email,
            name: name,
            password: password
        }, function (data) {
            if (data.status === "otp_resent") {
                alert("Nouveau code envoyé !");
            } else {
                alert("Erreur lors de l'envoi.");
            }
        });
    });
});
