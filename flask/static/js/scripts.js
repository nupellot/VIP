<script>
$(document).ready(function() {
    // Получаем данные через API
    $.getJSON('/api/data', function(data) {
        var experts = data.experts;
        var nominants = data.nominants;
        var votes = data.votes;
        var nominantStats = data.nominant_stats;

        // Заполнение оценок в таблице
        votes.forEach(function(vote) {
            var expertId = vote[0];
            var nominantId = vote[1];
            var rating = vote[2];

            $("#rating-" + nominantId + "-" + expertId).text(rating);
        });

        // Заполнение средней оценки и дисперсии для каждого номинанта
        nominants.forEach(function(nominant) {
            var nominantId = nominant[0];
            var avgRating = nominantStats[nominantId].avg.toFixed(2);
            var variance = nominantStats[nominantId].variance.toFixed(2);

            $("#avg-" + nominantId).text(avgRating);
            $("#variance-" + nominantId).text(variance);
        });

        // Теперь, когда все данные загружены, инициализируем DataTables
        $('#ratings-table').DataTable({
            "paging": true,
            "ordering": true,
            "info": false,
            "searching": false,
            "autoWidth": false,
            "columnDefs": [
                { "type": "num", "targets": "_all" }
            ]
        });
    });
});
</script>
