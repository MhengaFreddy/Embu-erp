const moduleContainer = document.getElementById('moduleContainer');

// Load dashboard widgets by default
window.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});

async function loadDashboardStats() {
    moduleContainer.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div class="bg-white p-4 rounded-lg shadow">
                <h3 class="text-gray-500 text-sm">Total Students</h3>
                <p id="totalStudents" class="text-2xl font-bold">--</p>
            </div>
            <div class="bg-white p-4 rounded-lg shadow">
                <h3 class="text-gray-500 text-sm">Fee Collection</h3>
                <p id="totalFees" class="text-2xl font-bold">KES --</p>
            </div>
            <div class="bg-white p-4 rounded-lg shadow">
                <h3 class="text-gray-500 text-sm">Staff Members</h3>
                <p id="totalStaff" class="text-2xl font-bold">--</p>
            </div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white p-4 rounded-lg shadow">
                <canvas id="enrollmentChart"></canvas>
            </div>
            <div class="bg-white p-4 rounded-lg shadow">
                <canvas id="revenueChart"></canvas>
            </div>
        </div>
    `;
    try {
        const stats = await fetchWithAuth('/api/dashboard/stats'); // assume endpoint exists
        document.getElementById('totalStudents').textContent = stats.total_students;
        document.getElementById('totalFees').textContent = 'KES ' + stats.fee_collected.toLocaleString();
        document.getElementById('totalStaff').textContent = stats.total_staff;
        // Render charts
        new Chart(document.getElementById('enrollmentChart'), { type: 'bar', data: { labels: stats.enrollment_labels, datasets: [{ label: 'Enrollments', data: stats.enrollment_data, backgroundColor: '#059669' }] } });
    } catch (error) {
        console.error(error);
    }
}

function loadModule(moduleName) {
    switch(moduleName) {
        case 'students':
            loadStudentModule();
            break;
        case 'academic':
            loadAcademicModule();
            break;
        case 'finance':
            loadFinanceModule();
            break;
        default:
            loadDashboardStats();
    }
}

function loadStudentModule() {
    moduleContainer.innerHTML = `
        <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-bold mb-4">Student Management</h2>
            <div id="studentTable"></div>
        </div>
    `;
    fetchWithAuth('/api/students/').then(data => {
        let html = `<table class="w-full table-auto"><thead><tr><th>Adm No</th><th>Name</th><th>Status</th><th>Actions</th></tr></thead><tbody>`;
        data.forEach(s => {
            html += `<tr><td>${s.admission_number}</td><td>${s.first_name} ${s.last_name}</td><td>${s.enrollment_status}</td><td><button class="text-emerald-600">Edit</button></td></tr>`;
        });
        html += `</tbody></table>`;
        document.getElementById('studentTable').innerHTML = html;
    });
}
// Other module loaders similarly...
