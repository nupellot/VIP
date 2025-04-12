// $(document).ready(function() {
//     // Получаем данные через API
//     $.getJSON('/api/data', function(data) {
//         var experts = data.experts;
//         var nominants = data.nominants;
//         var votes = data.votes;
//         var nominantStats = data.nominant_stats;

//         // Заполнение оценок в таблице
//         votes.forEach(function(vote) {
//             var expertId = vote[0];
//             var nominantId = vote[1];
//             var rating = vote[2];

//             // Устанавливаем текст в ячейку
//             var cellId = "#rating-" + nominantId + "-" + expertId;
//             $(cellId).text(rating);

//             // Изменяем фон в зависимости от значения
//             var color = getCellColor(rating);
//             $(cellId).css("background-color", color);
//         });

//         // Заполнение средней оценки и дисперсии для каждого номинанта
//         nominants.forEach(function(nominant) {
//             var nominantId = nominant[0];
//             var avgRating = nominantStats[nominantId].avg.toFixed(2);
//             var variance = nominantStats[nominantId].variance.toFixed(2);

//             $("#avg-" + nominantId).text(avgRating);
//             $("#variance-" + nominantId).text(variance);
//         });

//         // Теперь, когда все данные загружены, инициализируем DataTables
//         $('#ratings-table').DataTable({
//             "paging": true,
//             "ordering": true,
//             "info": false,
//             "searching": false,
//             "autoWidth": false,
//             "columnDefs": [
//                 { "type": "num", "targets": [1, 2, 3, 4] },  // Устанавливаем числовую сортировку для всех столбцов с оценками
//                 { "type": "string", "targets": [0] }  // Устанавливаем строковую сортировку для первого столбца
//             ]
//         });
//     });

//     // Функция для получения цвета фона ячейки на основе значения
//     function getCellColor(rating) {
//         var red = Math.max(0, 255 - (rating - 1) * 28);  // 1 -> красный, 10 -> зеленый
//         var green = Math.max(0, (rating - 1) * 28);  // 1 -> красный, 10 -> зеленый
//         var blue = 0;  // Для простоты убираем синий компонент

//         // Возвращаем цвет в формате RGB
//         return `rgb(${red}, ${green}, ${blue})`;
//     }
// });
