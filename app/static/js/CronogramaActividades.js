// Datos de eventos para cada día (en español e inglés)
const ctEventsData = {
    6: [
        {
            time: "09:00 - 10:00",
            title: {
                es: "Reunión de equipo",
                en: "Team meeting"
            },
            description: {
                es: "Revisión de proyectos en curso y planificación de la semana.",
                en: "Review of ongoing projects and week planning."
            },
            location: {
                es: "Sala de Conferencias A",
                en: "Conference Room A"
            }
        },
        {
            time: "10:30 - 11:30",
            title: {
                es: "Revisión de presupuesto",
                en: "Budget review"
            },
            description: {
                es: "Análisis del presupuesto del trimestre con el departamento financiero.",
                en: "Analysis of the quarter's budget with the finance department."
            },
            location: {
                es: "Oficina del Director",
                en: "Director's Office"
            }
        },
        {
            time: "14:00 - 15:30",
            title: {
                es: "Almuerzo con clientes",
                en: "Lunch with clients"
            },
            description: {
                es: "Almuerzo de trabajo con representantes de la empresa XYZ.",
                en: "Working lunch with representatives from XYZ company."
            },
            location: {
                es: "Restaurante Downtown",
                en: "Downtown Restaurant"
            }
        },
        {
            time: "16:00 - 17:00",
            title: {
                es: "Capacitación de nuevos software",
                en: "New software training"
            },
            description: {
                es: "Sesión de formación sobre las nuevas herramientas de productividad.",
                en: "Training session on new productivity tools."
            },
            location: {
                es: "Sala de Capacitación B",
                en: "Training Room B"
            }
        }
    ],
    7: [
        {
            time: "08:30 - 09:30",
            title: {
                es: "Desayuno de trabajo",
                en: "Working breakfast"
            },
            description: {
                es: "Coordinación con el equipo de marketing para la nueva campaña.",
                en: "Coordination with the marketing team for the new campaign."
            },
            location: {
                es: "Cafetería Central",
                en: "Central Cafeteria"
            }
        },
        {
            time: "10:30 - 12:00",
            title: {
                es: "Presentación de proyecto",
                en: "Project presentation"
            },
            description: {
                es: "Presentación del nuevo proyecto a los inversionistas.",
                en: "Presentation of the new project to investors."
            },
            location: {
                es: "Sala de Junta Principal",
                en: "Main Board Room"
            }
        },
        {
            time: "13:00 - 14:00",
            title: {
                es: "Revisión de contratos",
                en: "Contract review"
            },
            description: {
                es: "Revisión de los contratos con el departamento legal.",
                en: "Review of contracts with the legal department."
            },
            location: {
                es: "Oficina de Legal",
                en: "Legal Office"
            }
        },
        {
            time: "16:00 - 17:30",
            title: {
                es: "Capacitación de equipo",
                en: "Team training"
            },
            description: {
                es: "Capacitación sobre nuevos procedimientos de calidad.",
                en: "Training on new quality procedures."
            },
            location: {
                es: "Sala de Capacitación A",
                en: "Training Room A"
            }
        }
    ],
    8: [
        {
            time: "09:00 - 10:30",
            title: {
                es: "Conferencia virtual",
                en: "Virtual conference"
            },
            description: {
                es: "Participación en conferencia internacional sobre tendencias del sector.",
                en: "Participation in international conference on industry trends."
            },
            location: {
                es: "Online",
                en: "Online"
            }
        },
        {
            time: "11:00 - 12:30",
            title: {
                es: "Reunión de departamento",
                en: "Department meeting"
            },
            description: {
                es: "Reunión mensual de todo el departamento para alinear objetivos.",
                en: "Monthly meeting of the entire department to align objectives."
            },
            location: {
                es: "Auditorio Principal",
                en: "Main Auditorium"
            }
        },
        {
            time: "15:30 - 16:30",
            title: {
                es: "Revisión de documentos",
                en: "Document review"
            },
            description: {
                es: "Revisión de documentación técnica del proyecto Alpha.",
                en: "Review of technical documentation for Project Alpha."
            },
            location: {
                es: "Sala de Reuniones C",
                en: "Meeting Room C"
            }
        },
        {
            time: "17:00 - 18:00",
            title: {
                es: "Entrevista de trabajo",
                en: "Job interview"
            },
            description: {
                es: "Entrevista con candidatos para la posición de desarrollador senior.",
                en: "Interview with candidates for the senior developer position."
            },
            location: {
                es: "Oficina de RH",
                en: "HR Office"
            }
        }
    ],
    9: [
        {
            time: "09:30 - 11:00",
            title: {
                es: "Entrevistas de evaluación",
                en: "Evaluation interviews"
            },
            description: {
                es: "Entrevistas de evaluación de desempeño del personal.",
                en: "Performance evaluation interviews with staff."
            },
            location: {
                es: "Oficina de Evaluación",
                en: "Evaluation Office"
            }
        },
        {
            time: "11:30 - 13:00",
            title: {
                es: "Comité directivo",
                en: "Steering committee"
            },
            description: {
                es: "Reunión del comité directivo para revisión estratégica.",
                en: "Steering committee meeting for strategic review."
            },
            location: {
                es: "Sala de Junta Directiva",
                en: "Board Room"
            }
        },
        {
            time: "14:30 - 16:00",
            title: {
                es: "Sesión de brainstorming",
                en: "Brainstorming session"
            },
            description: {
                es: "Sesión creativa para el desarrollo de nuevas ideas de producto.",
                en: "Creative session for developing new product ideas."
            },
            location: {
                es: "Sala Creativa",
                en: "Creative Room"
            }
        },
        {
            time: "16:30 - 17:30",
            title: {
                es: "Reunión con proveedores",
                en: "Meeting with suppliers"
            },
            description: {
                es: "Reunión con proveedores para negociación de contratos.",
                en: "Meeting with suppliers for contract negotiation."
            },
            location: {
                es: "Sala de Reuniones B",
                en: "Meeting Room B"
            }
        }
    ],
    10: [
        {
            time: "10:00 - 11:30",
            title: {
                es: "Revisión semanal",
                en: "Weekly review"
            },
            description: {
                es: "Revisión de los avances y resultados de la semana.",
                en: "Review of the week's progress and results."
            },
            location: {
                es: "Sala de Conferencias A",
                en: "Conference Room A"
            }
        },
        {
            time: "12:00 - 13:30",
            title: {
                es: "Comida de equipo",
                en: "Team lunch"
            },
            description: {
                es: "Comida de integración y celebración de logros del equipo.",
                en: "Integration lunch and celebration of team achievements."
            },
            location: {
                es: "Restaurante La Terraza",
                en: "La Terraza Restaurant"
            }
        },
        {
            time: "15:00 - 16:00",
            title: {
                es: "Planificación próxima semana",
                en: "Next week planning"
            },
            description: {
                es: "Planificación detallada de actividades para la próxima semana.",
                en: "Detailed planning of activities for the next week."
            },
            location: {
                es: "Sala de Reuniones C",
                en: "Meeting Room C"
            }
        },
        {
            time: "17:00 - 18:00",
            title: {
                es: "Cierre de semana",
                en: "Week closing"
            },
            description: {
                es: "Sesión de cierre para revisar cumplimiento de objetivos.",
                en: "Closing session to review objective compliance."
            },
            location: {
                es: "Sala de Conferencias B",
                en: "Conference Room B"
            }
        }
    ]
};

// Obtener elementos del DOM
const ctDays = document.querySelectorAll('.ct-day');
const ctAgendaView = document.getElementById('ctAgendaView');
const ctAgendaTitle = document.getElementById('ctAgendaTitle');
const ctEventsList = document.getElementById('ctEventsList');
const ctCloseAgendaBtn = document.getElementById('ctCloseAgenda');

// Añadir event listeners a los días
ctDays.forEach(day => {
    day.addEventListener('click', () => {
        // Remover clase active de todos los días
        ctDays.forEach(d => d.classList.remove('active'));
        
        // Añadir clase active al día clickeado
        day.classList.add('active');
        
        // Mostrar la agenda para ese día
        const dayNumber = day.getAttribute('data-day');
        ctShowAgenda(dayNumber);
    });
});

// Función para mostrar la agenda de un día específico
function ctShowAgenda(dayNumber) {
    const dayEvents = ctEventsData[dayNumber];
    const dayNamesEs = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const dayNamesEn = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const date = new Date(2025, 9, dayNumber); // Octubre es el mes 9 (0-indexed)
    
    // Obtener el idioma actual
    const isEnglish = document.documentElement.classList.contains('lang-en');
    const dayName = isEnglish ? dayNamesEn[date.getDay()] : dayNamesEs[date.getDay()];
    
    // Actualizar título de la agenda
    const agendaTitleEs = `Agenda - ${dayName} ${dayNumber} de Octubre 2025`;
    const agendaTitleEn = `Agenda - ${dayName} October ${dayNumber}, 2025`;
    
    ctAgendaTitle.innerHTML = isEnglish ? 
        `<span class="i18n i18n-es">${agendaTitleEs}</span><span class="i18n i18n-en">${agendaTitleEn}</span>` :
        `<span class="i18n i18n-es">${agendaTitleEs}</span><span class="i18n i18n-en">${agendaTitleEn}</span>`;
    
    // Limpiar lista de eventos
    ctEventsList.innerHTML = '';
    
    // Añadir eventos a la lista
    dayEvents.forEach(event => {
        const [startTime, endTime] = event.time.split(' - ');
        
        const eventElement = document.createElement('div');
        eventElement.className = 'ct-event-item';
        eventElement.innerHTML = `
            <div class="ct-event-time-large">
                <div class="ct-event-hour">${startTime}</div>
                <div class="ct-event-duration">${endTime}</div>
            </div>
            <div class="ct-event-details">
                <h3 class="ct-event-title">
                    <span class="i18n i18n-es">${event.title.es}</span>
                    <span class="i18n i18n-en">${event.title.en}</span>
                </h3>
                <p class="ct-event-description">
                    <span class="i18n i18n-es">${event.description.es}</span>
                    <span class="i18n i18n-en">${event.description.en}</span>
                </p>
                <div class="ct-event-location">
                    <i class="fas fa-map-marker-alt"></i> 
                    <span class="i18n i18n-es">${event.location.es}</span>
                    <span class="i18n i18n-en">${event.location.en}</span>
                </div>
            </div>
        `;
        
        ctEventsList.appendChild(eventElement);
    });
    
    // Mostrar la vista de agenda
    ctAgendaView.classList.add('active');
    
    // Desplazar hacia la agenda
    ctAgendaView.scrollIntoView({ behavior: 'smooth' });
}

// Event listener para el botón de cerrar agenda
ctCloseAgendaBtn.addEventListener('click', () => {
    ctAgendaView.classList.remove('active');
    ctDays.forEach(day => day.classList.remove('active'));
});

// Cerrar agenda al hacer clic fuera de ella
document.addEventListener('click', (e) => {
    if (ctAgendaView.classList.contains('active') && 
        !ctAgendaView.contains(e.target) && 
        !Array.from(ctDays).some(day => day.contains(e.target))) {
        ctAgendaView.classList.remove('active');
        ctDays.forEach(day => day.classList.remove('active'));
    }
});

// Inicializar con el día actual (6 de octubre) si está en el rango
const currentDate = new Date();
if (currentDate.getFullYear() === 2025 && currentDate.getMonth() === 9 && currentDate.getDate() >= 6 && currentDate.getDate() <= 10) {
    const currentDay = currentDate.getDate();
    document.querySelector(`.ct-day[data-day="${currentDay}"]`).click();
}