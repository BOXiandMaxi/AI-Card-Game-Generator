// Global variables
let selectedPack = null;
let cardPower = null;

// Initialize the application
$(document).ready(function() {
    initializePackSelection();
    initializeButtons();
    // [NEW] เริ่มต้นระบบปุ่มสลับ Device
    initializeDeviceSwitch();
    console.log("System Ready: Script Loaded Correctly");
});

function checkSystemCapabilities() {
    $.ajax({
        url: "/check_gpu_status", // เดี๋ยวเราไปสร้าง Route นี้
        type: "GET",
        success: function(data) {
            if (data.has_gpu) {
                // ถ้ามี GPU ค่อยโชว์ปุ่ม
                $('.device-switch-wrapper').css('display', 'flex');
            }
        }
    });
}

// [NEW] ฟังก์ชันจัดการปุ่มสลับ CPU/GPU
function initializeDeviceSwitch() {
    // 1. ตั้งค่าเริ่มต้น (สมมติว่าเซิฟเวอร์เริ่มที่ CPU หรือตาม Config)
    // ถ้าคุณตั้งใน python ว่าเริ่มเป็น GPU, ให้ใส่ $('#gpuToggle').prop('checked', true);
    // แต่ถ้าเริ่มเป็น CPU ก็ปล่อยไว้
    
    // 2. ดักจับการกดปุ่ม
    $('#gpuToggle').on('change', function() {
        const isGPU = $(this).is(':checked');
        const mode = isGPU ? 'gpu' : 'cpu';

        // โชว์ Loading เพราะการย้าย Model ใช้เวลา
        $('#loadingOverlay').removeClass('hidden');
        $('#loadingText').text(isGPU ? "SWITCHING TO GPU POWER..." : "SWITCHING BACK TO CPU...");

        // ส่งคำสั่งไป Server
        $.ajax({
            url: "/switch_device",
            type: "POST",
            data: { mode: mode },
            success: function(response) {
                $('#loadingOverlay').addClass('hidden');
                
                if (response.status === 'success') {
                    // Alert เท่ๆ หรือแค่ Log ก็ได้
                    console.log(response.message);
                } else {
                    alert("Error: " + response.message);
                    // ดีดปุ่มกลับคืนค่าเดิมถ้า Error
                    $('#gpuToggle').prop('checked', !isGPU); 
                }
            },
            error: function() {
                $('#loadingOverlay').addClass('hidden');
                alert("Server Connection Failed");
                $('#gpuToggle').prop('checked', !isGPU);
            }
        });
    });
}

// Pack Selection
function initializePackSelection() {
    $('.pack-card').on('click', function() {
        $('.pack-card').removeClass('selected');
        $(this).addClass('selected');
        selectedPack = $(this).data('pack');
        $('#openPackBtn').prop('disabled', false);
    });
}

// Button Handlers
function initializeButtons() {
    $('#openPackBtn').on('click', openCardPack);
    $('#confirmBtn').on('click', confirmSelection);
    $('#classSelect').on('change', onClassSelectChange);
}

// Open Card Pack
function openCardPack() {
    if (!selectedPack) {
        alert('Please select a card pack first!');
        return;
    }

    $.ajax({
        url: "/open_card_pack",
        type: "POST",
        data: { card_pack: selectedPack },
        success: function(data) {
            console.log("Card Pack opened:", data.card_pack);
            cardPower = data.card_power;
            showClassAndWeaponSelection();
        },
        error: function(xhr, status, error) {
            console.error("Error opening card pack:", error);
            alert("Failed to open card pack. Please try again.");
        }
    });
}

// Show Class and Weapon Selection
function showClassAndWeaponSelection() {
    $('#classSelection').removeClass('hidden');
    
    // Smooth scroll
    $('html, body').animate({
        scrollTop: $('#classSelection').offset().top - 50
    }, 800);

    getClasses();
    $('#weaponSelect').html("<option value=''>-- Select Weapon --</option>");
}

// Class Select Change Handler
function onClassSelectChange() {
    const selectedClass = $('#classSelect').val();
    if (selectedClass) {
        getWeapons(selectedClass);
    } else {
        $('#weaponSelect').html("<option value=''>-- Select Weapon --</option>");
    }
}

// Get Classes from Server
function getClasses() {
    $.ajax({
        url: "/get_classes",
        type: "GET",
        success: function(data) {
            populateDropdown('classSelect', data.classes);
        }
    });
}

// Get Weapons from Server
function getWeapons(selectedClass) {
    $.ajax({
        url: "/get_weapons/" + selectedClass,
        type: "GET",
        success: function(data) {
            populateDropdown('weaponSelect', data.weapons);
        }
    });
}

// Populate Dropdown
function populateDropdown(dropdownId, options) {
    const dropdown = $('#' + dropdownId);
    const label = dropdownId === 'classSelect' ? 'Class' : 'Weapon';
    
    dropdown.html(`<option value="">-- Select ${label} --</option>`);
    options.forEach(function(option) {
        dropdown.append(`<option value="${option}">${option}</option>`);
    });
}

// ----------------------------------------------------------------------
// [แก้ใหม่] ฟังก์ชันยืนยันและเริ่มระบบ 3D Flip
// ----------------------------------------------------------------------
function confirmSelection() {
    const selectedClass = $('#classSelect').val();
    const selectedWeapon = $('#weaponSelect').val();

    if (!selectedPack || !selectedClass || !selectedWeapon) {
        alert("Please select a Card Pack, Class, and Weapon before confirming your selection.");
        return;
    }

    // 1. เปิด Loading
    $('#loadingOverlay').removeClass('hidden');
    
    // สุ่มข้อความเท่ๆ
    const loadingMessages = [
        "Summoning Creature...",
        "Infusing Elemental Magic...",
        "Constructing Reality...",
        "Connecting to Neural Network...",
        "Gathering Mana..."
    ];
    $('#loadingText').text(loadingMessages[Math.floor(Math.random() * loadingMessages.length)]);

    // 2. Reset ฉากการ์ดให้พร้อมสำหรับการเปิดใหม่ (สำคัญ!)
    $('#resultContainer').addClass('hidden'); // ซ่อนผลลัพธ์เก่า
    $('#flipCard').removeClass('is-flipped'); // จับการ์ดหันหลัง
    $('#godAura').addClass('hidden');         // ปิดออร่า
    $('#cardStats').addClass('hidden');       // ซ่อนสเตตัส
    $('#resetButtonContainer').addClass('hidden'); // ซ่อนปุ่ม

    // ยิงคำสั่งไป Server
    $.ajax({
        url: "/confirm_selection",
        type: "POST",
        data: {
            card_pack: selectedPack,
            selected_class: selectedClass,
            selected_weapon: selectedWeapon
        },
        success: function(data) {
            console.log("Selection confirmed:", data);

            // 3. เทคนิค Preload: รอโหลดรูปให้เสร็จก่อน ค่อยปิด Loading
            // ถ้าไม่ทำแบบนี้ รูปบนการ์ดจะขาวโพลนตอนเปิด
            if (data.card_url) {
                const img = new Image();
                const timestamp = new Date().getTime(); // แก้ Cache
                const finalUrl = data.card_url + "?t=" + timestamp;

                img.onload = function() {
                    // รูปมาแล้ว -> ปิด Loading -> ตั้งค่าฉาก 3D
                    $('#loadingOverlay').addClass('hidden');
                    setup3DScene(data, finalUrl);
                };
                img.onerror = function() {
                    // ถ้ารูปพัง ก็ยังต้องไปต่อ
                    $('#loadingOverlay').addClass('hidden');
                    setup3DScene(data, finalUrl);
                };
                img.src = finalUrl;
            }
        },
        error: function(xhr, status, error) {
            $('#loadingOverlay').addClass('hidden');
            console.error("Error confirming selection:", error);
            alert("Failed to confirm selection. Check Server Logs.");
        }
    });
}

// ----------------------------------------------------------------------
// [ฟังก์ชันใหม่] จัดการฉาก 3D และการคลิกเปิดการ์ด
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// [แก้ใหม่ล่าสุด] ระบบเปิด-ปิดการ์ดไปมา (Toggle Flip)
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// [FIXED] แก้ปัญหาการ์ดก้มหน้า (คำนวณจากจุดกึ่งกลางการ์ด)
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// [FINAL GOD MODE] หมุนรอบทิศ 360 (ระบบ Trackball) + ไม่ติดขอบจอ
// ----------------------------------------------------------------------
function setup3DScene(data, imageUrl) {
    // Reset Class และใส่ Rank
    $('#flipCard').attr('class', 'card-object'); 
    $('#flipCard').addClass('rank-' + data.card_pack);
    $('#flipCard').removeAttr('style');

    // ใส่ข้อมูล HTML
    $('#resultPack').text(selectedPack.toUpperCase());
    $('#resultClass').text($('#classSelect').val());
    $('#resultWeapon').text($('#weaponSelect').val());
    $('#resultPower').text(data.card_power || '--');
    $('#cardImage').attr('src', imageUrl);

    // โชว์เวที
    $('#resultContainer').removeClass('hidden');

    $('html, body').animate({
        scrollTop: $('#resultContainer').offset().top - 50
    }, 800);

    // --- ตัวแปรควบคุมระบบหมุน ---
    let isFlipped = false;     // สถานะว่าเปิดการ์ดอยู่ไหม (Base State)
    let isDragging = false;    // กำลังกดลากไหม
    
    let lastMouseX, lastMouseY; // ตำแหน่งเมาส์ล่าสุด
    let currentRotateX = 0;     // องศาแกน X ปัจจุบัน (ก้มเงย)
    let currentRotateY = 0;     // องศาแกน Y ปัจจุบัน (หมุนซ้ายขวา)
    let hasMoved = false;       // เช็คว่าลากจริงไหม (เพื่อแยกกับคลิก)

    const card = $('#flipCard');
    const scene = $('.card-scene');

    // ============================================================
    // 1. เริ่มกดเมาส์ (JAB)
    // ============================================================
    scene.off('mousedown').on('mousedown', function(e) {
        e.preventDefault();
        isDragging = true;
        hasMoved = false;
        
        // จำตำแหน่งเมาส์เริ่มต้น
        lastMouseX = e.pageX;
        lastMouseY = e.pageY;
        
        // หยุด Transition ชั่วคราวเพื่อให้ลากติดมือ (Real-time)
        card.addClass('is-interacting');
    });

    // ============================================================
    // 2. ลากเมาส์ (SWIPE) - ใช้หลักการ "ขยับไปเท่าไหร่ บวกเพิ่มเท่านั้น"
    // ============================================================
    $(window).off('mousemove').on('mousemove', function(e) {
        if (!isDragging) return;

        const deltaX = e.pageX - lastMouseX; // เมาส์ขยับแนวนอนไปเท่าไหร่
        const deltaY = e.pageY - lastMouseY; // เมาส์ขยับแนวตั้งไปเท่าไหร่

        // ถ้าขยับน้อยๆ ถือว่ามือสั่น ไม่นับ
        if (Math.abs(deltaX) > 1 || Math.abs(deltaY) > 1) {
            hasMoved = true;
        }

        // ความไวในการหมุน (ปรับเลข 0.5 ได้ถ้าอยากให้ไวขึ้น/ช้าลง)
        const speed = 0.5;

        // บวกองศาเพิ่มเข้าไป (Accumulate)
        currentRotateY += deltaX * speed; 
        currentRotateX -= deltaY * speed; // ลบเพราะเมาส์ลงต้องให้เงยหน้า (Invert)

        // อัปเดตตำแหน่งเมาส์ล่าสุด เพื่อใช้คำนวณรอบถัดไป
        lastMouseX = e.pageX;
        lastMouseY = e.pageY;

        // คำนวณฐานการหมุน (ถ้าเปิดอยู่ ฐานคือ 0, ถ้าปิดอยู่ ฐานคือ 180)
        let baseRotate = isFlipped ? 0 : 180;

        // สั่งหมุน!
        card.css('transform', `rotateY(${baseRotate + currentRotateY}deg) rotateX(${currentRotateX}deg) scale(1.02)`);
    });

    // ============================================================
    // 3. ปล่อยเมาส์ (RELEASE)
    // ============================================================
    $(window).off('mouseup').on('mouseup', function() {
        if (!isDragging) return;
        isDragging = false;
        
        // คืนค่า Transition ให้ CSS จัดการต่อ
        card.removeClass('is-interacting');

        if (!hasMoved) {
            // --- กรณี: คลิกเฉยๆ (ไม่ได้ลาก) -> ให้พลิกการ์ด ---
            toggleFlip();
        } else {
            // --- กรณี: ลากเสร็จแล้วปล่อย -> ให้เด้งกลับท่าสวยๆ ---
            
            // รีเซ็ตค่าองศาที่ทดไว้ เพื่อให้กลับสู่ท่ามาตรฐาน
            currentRotateX = 0;
            currentRotateY = 0;
            
            // ลบ Style inline ออก เพื่อให้ CSS ดึงกลับไปที่ 0 หรือ 180 เอง
            card.removeAttr('style');
        }
    });

    // ฟังก์ชันพลิกการ์ด (เหมือนเดิม)
    // ฟังก์ชันพลิกการ์ด (แก้เรื่องวาร์ป/ส่องกระจก)
    function toggleFlip() {
        // 1. สำคัญมาก: เอาคลาส is-interacting ออก เพื่อให้ Transition (อนิเมชั่น) กลับมาทำงาน
        card.removeClass('is-interacting');

        // 2. ล้างค่ามุมที่บิดค้างไว้จากการลากเมาส์
        currentRotateX = 0;
        currentRotateY = 0;
        
        // 3. ลบ Inline Style (ที่เกิดจากการลาก) ทิ้ง
        // พอ Style หายไป + อนิเมชั่นกลับมาทำงาน -> มันจะค่อยๆ หมุนกลับไปท่ามาตรฐานเอง
        card.removeAttr('style'); 

        // 4. สลับสถานะ (หน้า/หลัง)
        isFlipped = !isFlipped;
        
        // 5. สั่งหมุนด้วย CSS Class
        // จังหวะนี้แหละครับ ที่มันจะค่อยๆ หมุนนุ่มๆ เพราะเราเอา is-interacting ออกไปแล้วในข้อ 1
        card.toggleClass('is-flipped', isFlipped);

        // Logic เดิม: โชว์/ซ่อน ปุ่มและสเตตัส
        if (isFlipped) {
            $('#godAura').removeClass('hidden');
            setTimeout(function() {
                // เช็คอีกทีกันพลาด (เผื่อคนกดรัว)
                if (card.hasClass('is-flipped')) {
                    $('#cardStats').removeClass('hidden').hide().fadeIn(1000);
                    $('#resetButtonContainer').removeClass('hidden').hide().fadeIn(2000);
                }
            }, 600); // ลดเวลาลงนิดนึงให้สัมพันธ์กับ animation css
        } else {
            $('#godAura').addClass('hidden');
            $('#cardStats').addClass('hidden');
            $('#resetButtonContainer').addClass('hidden');
        }
    }
}