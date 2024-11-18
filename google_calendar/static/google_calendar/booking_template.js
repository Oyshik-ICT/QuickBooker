$(document).ready(function () {
    let selectedDuration = null;
    let selectedDate = null;
    let selectedTime = null;

    // Duration Selection
    $('.duration-option').click(function () {
        $('.duration-option').removeClass('selected');
        $(this).addClass('selected');
        selectedDuration = parseInt($(this).data('duration'));

        // Reset subsequent selections
        $('.date-tab').removeClass('selected');
        $('.time-slot').removeClass('selected');
        $('.time-slots').removeClass('active');
        $('#booking-form').hide();
        updateSelectedInfo();
    });

    // Date Selection
    $('.date-tab').click(function () {
        if (!selectedDuration) {
            alert('Please select a session duration first.');
            return;
        }

        $('.date-tab').removeClass('selected');
        $(this).addClass('selected');

        const selectedDateValue = $(this).data('date');
        $('.time-slots').removeClass('active');
        $(`.time-slots[data-date="${selectedDateValue}"]`).addClass('active');

        selectedDate = $(this).text().trim();
        $('.time-slot').removeClass('selected');
        $('#booking-form').hide();
        updateSelectedInfo();
    });

    // Time Selection
    $('.time-slot').click(function () {
        if (!selectedDuration) {
            alert('Please select a session duration first.');
            return;
        }
        if (!$('.date-tab.selected').length) {
            alert('Please select a date first.');
            return;
        }

        $('.time-slot').removeClass('selected');
        $(this).addClass('selected');

        selectedTime = $(this).data('time');
        const selectedDateTab = $('.date-tab.selected');
        const startDate = selectedDateTab.data('date').split(' ')[0];

        $('#start_date').val(startDate);
        $('#start_time').val(selectedTime);
        $('#session_duration').val(selectedDuration);

        $('#booking-form').slideDown();
        updateSelectedInfo();

        // Scroll to booking form
        $('html, body').animate({
            scrollTop: $('#booking-form').offset().top - 20
        }, 500);
    });

    // Form Submission
    $('#appointment-form').submit(function (e) {
        e.preventDefault();

        const submitButton = $('#submit-button');
        submitButton.prop('disabled', true).text('Booking...');

        $.ajax({
            url: '/book-appointment/',
            type: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                if (response.status === 'success') {
                    showMessage(response.message, 'success');
                    $('#appointment-form')[0].reset();
                    setTimeout(() => {
                        location.reload();
                    }, 3000);
                } else {
                    showMessage(response.message, 'error');
                }
            },
            error: function (xhr) {
                let errorMessage = 'An error occurred while booking the appointment.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                }
                showMessage(errorMessage, 'error');
            },
            complete: function () {
                submitButton.prop('disabled', false).text('Book Appointment');
            }
        });
    });

    // Helper Functions
    function updateSelectedInfo() {
        $('#selected-slot-display').text(selectedDate || 'Not selected');
        $('#selected-time-display').text(selectedTime ? formatTime(selectedTime) : 'Not selected');
        $('#selected-duration-display').text(selectedDuration ? `${selectedDuration} minutes` : 'Not selected');
    }

    function formatTime(time) {
        const [hours, minutes] = time.split(':');
        const date = new Date();
        date.setHours(parseInt(hours));
        date.setMinutes(parseInt(minutes));
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    function showMessage(message, type) {
        const messageDiv = $('#message');
        messageDiv.removeClass('success error').addClass(type).html(message).show();
    }

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Add CSRF token to AJAX requests
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
});