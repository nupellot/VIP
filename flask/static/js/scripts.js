$(document).ready(function() {
    // Получаем данные через API
    $.getJSON('/api/data', function(data) {
        // Преобразуем оценки в таблицу
        var experts = data.experts;
        var nominants = data.nominants;
        var votes = data.votes;

        // Перебираем все оценки и вставляем их в таблицу
        votes.forEach(function(vote) {
            var expertId = vote[0];
            var nominantId = vote[1];
            var rating = vote[2];
            
            // Ищем соответствующую ячейку в таблице
            var cellId = "#rating-" + nominantId + "-" + expertId;
            $(cellId).text(rating);
        });
    });
});
