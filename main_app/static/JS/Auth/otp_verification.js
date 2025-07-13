document.addEventListener('DOMContentLoaded', function() {
            // OTP input handling
            const otpInputs = document.querySelectorAll('.otp-input');
            const fullOtpInput = document.getElementById('fullOtp');
            
            // Handle OTP input navigation
            otpInputs.forEach((input, index) => {
                input.addEventListener('input', (e) => {
                    // Only allow numbers
                    e.target.value = e.target.value.replace(/[^0-9]/g, '');
                    
                    // Auto focus to next input
                    if (e.target.value.length === 1 && index < otpInputs.length - 1) {
                        otpInputs[index + 1].focus();
                    }
                    
                    updateFullOtp();
                });
                
                // Handle backspace
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Backspace' && e.target.value.length === 0 && index > 0) {
                        otpInputs[index - 1].focus();
                    }
                });
            });
            
            // Update the hidden full OTP field
            function updateFullOtp() {
                let otp = '';
                otpInputs.forEach(input => {
                    otp += input.value;
                });
                fullOtpInput.value = otp;
            }
    window.onload = function () {
        document.getElementById("otp1").focus();
    };
        });