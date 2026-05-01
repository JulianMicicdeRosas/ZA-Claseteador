<?php
/**
 * Plugin Name: Permitir subida de HTML para administradores
 * Description: Habilita la subida de archivos .html a la biblioteca de medios. Solo para administradores. Requerido por la app de transcripción de clases del Zorro Azul.
 * Version:     1.0.0
 * Author:      El Zorro Azul
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

add_filter( 'upload_mimes', function ( $mimes ) {
    if ( current_user_can( 'manage_options' ) ) {
        $mimes['html'] = 'text/html';
        $mimes['htm']  = 'text/html';
    }
    return $mimes;
} );

add_filter( 'wp_check_filetype_and_ext', function ( $data, $file, $filename, $mimes ) {
    if ( ! current_user_can( 'manage_options' ) ) {
        return $data;
    }

    $filetype = wp_check_filetype( $filename, $mimes );

    if ( 'html' === strtolower( $filetype['ext'] ) || 'htm' === strtolower( $filetype['ext'] ) ) {
        $data['ext']             = $filetype['ext'];
        $data['type']            = 'text/html';
        $data['proper_filename'] = $filename;
    }

    return $data;
}, 10, 4 );
