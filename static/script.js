$(document).ready(function () {
    const $pdfSelect = $('#pdf-select');
    const $referenceOptions = $('#reference-options');
    const $dropdowns = $('#dropdowns');
    const $partDropdown = $('#part-dropdown');
    const $sectionDropdown = $('#section-dropdown');
    const $subsectionDropdown = $('#subsection-dropdown');
    const $partSelect = $('#part-select');
    const $sectionSelect = $('#section-select');
    const $subsectionSelect = $('#subsection-select');
    const $submitBtn = $('#submit-btn');
    let urls = {};

    // Hide reference options and dropdowns initially
    $referenceOptions.hide();
    $dropdowns.hide();

    // Fetch URLs from the JSON file
    $.getJSON('/static/pdf_urls.json', function (data) {
        urls = data.urls;
    });

    // Show reference options once a PDF is selected
    $pdfSelect.change(function () {
        $referenceOptions.toggle(!!$(this).val());
        $dropdowns.hide();
    });

    // Handle radio button changes
    $('input[name="reference-type"]').change(function () {
        const selectedType = $(this).val();
        $dropdowns.find('> div').hide();
        $submitBtn.prop('disabled', true);
        $('label').removeClass('disabled-label');
        $('select').prop('disabled', false).removeClass('disabled-select');

        if (selectedType === 'part' || selectedType === 'section' || selectedType === 'subsection') {
            $partDropdown.show();
            if (selectedType === 'section' || selectedType === 'subsection') {
                $sectionDropdown.show();
                $sectionSelect.prop('disabled', true).addClass('disabled-select');
            }
            if (selectedType === 'subsection') {
                $subsectionDropdown.show();
                $subsectionSelect.prop('disabled', true).addClass('disabled-select');
            }
            populateParts();
        }
    });

    // Function to populate parts based on selected PDF
    function populateParts() {
        const pdfFile = $pdfSelect.val();
        if (pdfFile) {
            $.post('/get_part_titles', { pdf_file: pdfFile }, function (response) {
                $partSelect.empty().html('<option value="" selected disabled>--Select Part--</option>');
                response.forEach(part => {
                    $partSelect.append(`<option value="${part.title}" data-page="${part.page_number}">${part.title}</option>`);
                });
                $partDropdown.show();
                $dropdowns.show();
            });
        }
    }

    // Handle change event for part select dropdown
    $partSelect.change(function () {
        const selectedPart = $(this).val();
        $sectionSelect.prop('disabled', !selectedPart).toggleClass('disabled-select', !selectedPart);
        $subsectionSelect.prop('disabled', !selectedPart).toggleClass('disabled-select', !selectedPart);
        $subsectionSelect.html('<option value="" selected disabled>--Select Subsection--</option>');
        if (selectedPart) populateSections(selectedPart);
    });

    // Function to populate sections based on selected part
    function populateSections(selectedPart) {
        const pdfFile = $pdfSelect.val();
        $.get('/get_sections', { pdf_selected: pdfFile, part_selected: selectedPart }, function (response) {
            $sectionSelect.empty().html('<option value="" selected disabled>--Select Section--</option>').append(response);
        });
    }

    // Handle change event for section select dropdown
    $sectionSelect.change(function () {
        const selectedSection = $(this).find('option:selected').text();
        $subsectionSelect.prop('disabled', !selectedSection).toggleClass('disabled-select', !selectedSection);
        if (selectedSection) populateSubsections(selectedSection);
    });

    // Function to populate subsections based on selected section
    function populateSubsections(selectedSection) {
        const pdfFile = $pdfSelect.val();
        $.get('/get_subsections', { pdf_selected: pdfFile, section_selected: selectedSection }, function (response) {
            $subsectionSelect.empty().html('<option value="" selected disabled>--Select Subsection--</option>').append(response);
        });
    }

    // Handle submit button state based on form validity
    $pdfSelect.add('input[name="reference-type"]').add($partSelect).add($sectionSelect).add($subsectionSelect).change(function () {
        const pdfSelected = $pdfSelect.val();
        const referenceType = $('input[name="reference-type"]:checked').val();
        const partSelected = $partSelect.val();
        const sectionSelected = $sectionSelect.val();
        const subsectionSelected = $subsectionSelect.val();
        const isValid = pdfSelected && referenceType && partSelected &&
            (referenceType !== 'section' || sectionSelected) &&
            (referenceType !== 'subsection' || (sectionSelected && subsectionSelected));
        $submitBtn.prop('disabled', !isValid);
    }).change();

    // Event listener for submit button click
    $submitBtn.click(function (e) {
        e.preventDefault();
        const pdfName = $pdfSelect.val();
        const referenceType = $('input[name="reference-type"]:checked').val();
        const pageNumber = referenceType === 'part' ? $partSelect.find('option:selected').attr('data-page') : $(`#${referenceType}-select`).val();
        const fullUrl = urls[pdfName] + `#page=${pageNumber}`;
        if (pdfName in urls) window.open(fullUrl, '_blank');
        else alert('PDF link not found.');
    });
});