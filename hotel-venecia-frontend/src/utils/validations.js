export const globalValidations = {
    // Validar que un campo no esté vacío
    required: (value) => value && value.toString().trim().length > 0,
    
    // Validar DNI Peruano (8 dígitos)
    isDNI: (value) => /^\d{8}$/.test(value),
    
    // Validar RUC (11 dígitos)
    isRUC: (value) => /^\d{11}$/.test(value),
    
    // Validar solo letras (para nombres)
    onlyLetters: (value) => /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value),
};