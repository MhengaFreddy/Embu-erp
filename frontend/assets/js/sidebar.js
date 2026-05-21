document.addEventListener('DOMContentLoaded', function () {
    var user = JSON.parse(localStorage.getItem('user'));
    if (!user) { window.location.href = '/index.html'; return; }
    var role = user.role;
    var menus = {
        student: [
            { text: 'Dashboard', href: '/student_portal.html' },
            { text: 'Finance', href: '/pages/student/finance.html' },
            { text: 'Academics', href: '/pages/student/academics.html' },
            { text: 'Accommodation', href: '/pages/student/accommodation.html' },
            { text: 'Student Requests', href: '/pages/student/requests.html' },
            { text: 'Library', href: '/pages/student/library.html' }
        ]
    };
    var items = menus[role] || [];
    var html = '<h1 class="text-xl font-bold mb-8">Embu College</h1><nav class="space-y-2">';
    items.forEach(function (item) {
        html += '<a href="' + item.href + '" class="block py-2 px-3 rounded hover:bg-emerald-700">' + item.text + '</a>';
    });
    html += '</nav><div class="mt-auto pt-8"><button onclick="logout()" class="w-full bg-red-500 hover:bg-red-600 text-white py-2 rounded">Logout</button></div>';
    document.getElementById('sidebarContainer').innerHTML = html;
});

function logout() { localStorage.clear(); window.location.href = '/index.html'; }