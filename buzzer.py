class Buzzer:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.reactor = self.printer.get_reactor()

        # Настройка пина через pins Klipper
        ppins = self.printer.lookup_object('pins')
        self.pin = ppins.setup_pin('digital_out', config.get('pin'))

        # Состояние
        self.enabled = True
        self.is_active = False

        # Регистрация команд GCODE
        self.gcode.register_command('BUZZER_ENABLE', self.cmd_BUZZER_ENABLE,
                                    desc=self.cmd_BUZZER_ENABLE_help)
        self.gcode.register_command('BUZZER_DISABLE', self.cmd_BUZZER_DISABLE,
                                    desc=self.cmd_BUZZER_DISABLE_help)
        self.gcode.register_command('BUZZ_START', self.cmd_BUZZ_START,
                                    desc=self.cmd_BUZZ_START_help)
        self.gcode.register_command('BUZZ_END', self.cmd_BUZZ_END,
                                    desc=self.cmd_BUZZ_END_help)
        self.gcode.register_command('BUZZ_ERROR', self.cmd_BUZZ_ERROR,
                                    desc=self.cmd_BUZZ_ERROR_help)

        self.printer.register_event_handler("klippy:shutdown", self._shutdown)

    def _shutdown(self):
        """Выключение при завершении работы"""
        print_time = self.reactor.monotonic() + 0.5
        self.pin.set_digital(print_time, 0)

    def _beep(self, on_time, off_time, count=1):
        """Простой бип"""
        if not self.enabled:
            return

        def beep_callback(eventtime):
            print_time = eventtime
            for i in range(count):
                # Включить
                self.pin.set_digital(print_time, 1)
                print_time += on_time
                self.reactor.pause(print_time)

                # Выключить (кроме последнего бипа)
                if i < count - 1:
                    self.pin.set_digital(print_time, 0)
                    print_time += off_time
                    self.reactor.pause(print_time)

            # Гарантированно выключить после последнего бипа
            self.pin.set_digital(print_time, 0)
            return self.reactor.NEVER

        self.reactor.register_callback(beep_callback)

    cmd_BUZZER_ENABLE_help = "Включение звуковых сигналов"
    def cmd_BUZZER_ENABLE(self, gcmd):
        self.enabled = True
        gcmd.respond_info("Звуковые сигналы включены")

    cmd_BUZZER_DISABLE_help = "Выключение звуковых сигналов"
    def cmd_BUZZER_DISABLE(self, gcmd):
        self.enabled = False
        # Немедленное выключение
        print_time = self.reactor.monotonic() + 0.5
        self.pin.set_digital(print_time, 0)
        gcmd.respond_info("Звуковые сигналы выключены")

    cmd_BUZZ_START_help = "Воспроизведение мелодии начала печати"
    def cmd_BUZZ_START(self, gcmd):
        # 3 быстрых бипа
        self._beep(0.1, 0.05, 3)
        gcmd.respond_info("Мелодия начала печати")

    cmd_BUZZ_END_help = "Воспроизведение мелодии окончания печати"
    def cmd_BUZZ_END(self, gcmd):
        # 2 длинных бипа
        self._beep(0.3, 0.1, 2)
        gcmd.respond_info("Мелодия окончания печати")

    cmd_BUZZ_ERROR_help = "Воспроизведение мелодии ошибки"
    def cmd_BUZZ_ERROR(self, gcmd):
        # 5 очень быстрых бипов
        self._beep(0.05, 0.05, 5)
        gcmd.respond_info("Мелодия ошибки")

def load_config(config):
    return Buzzer(config)
