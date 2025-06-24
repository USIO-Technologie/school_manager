$(document).ready(function () {
    $('form.my-4').on('submit', function (e) {
        e.preventDefault();

        let $form = $(this);
        let data = $form.serialize();

        $.ajax({
            url: $form.attr('action') || window.location.pathname,
            type: 'POST',
            data: data,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (response) {
                $('.alert-danger, .alert-info').remove();

                if (response.redirect || response.redirect_url) {
                    window.location.href = response.redirect || response.redirect_url;
                    return;
                }

                if (response.error) {
                    $form.prepend('<div class="alert alert-danger">' + response.error + '</div>');
                }
                if (response.info) {
                    $form.prepend('<div class="alert alert-info">' + response.info + '</div>');
                }

                // Affichage dynamique du champ OTP si nécessaire
                if (response.otp_required) {
                    $form.find('input[name="username"]').prop('readonly', true);
                    $form.find('input[name="password"]').closest('.form-group').hide();

                    // Ajoute le champ OTP s'il n'existe pas déjà
                    if ($form.find('input[name="otp"]').length === 0) {
                        let otpField = `
                        <div class="form-group mb-2" id="otp-field">
                            <label class="form-label" for="otpInput">Code OTP</label>
                            <input type="text" class="form-control" id="otpInput" name="otp" placeholder="Code OTP"
                                autocomplete="one-time-code" inputmode="numeric" pattern="\\d*" required>
                        </div>`;
                        $form.find('.form-group').last().before(otpField);
                    }
                    $form.find('button[type="submit"]').text('Valider le code OTP');
                }
            },
            error: function () {
                $form.prepend('<div class="alert alert-danger">Erreur serveur, veuillez réessayer.</div>');
            }
        });
    });
});