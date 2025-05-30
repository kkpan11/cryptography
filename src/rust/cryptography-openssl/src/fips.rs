// This file is dual licensed under the terms of the Apache License, Version
// 2.0, and the BSD License. See the LICENSE file in the root of this repository
// for complete details.

#[cfg(all(
    CRYPTOGRAPHY_OPENSSL_300_OR_GREATER,
    not(any(
        CRYPTOGRAPHY_IS_LIBRESSL,
        CRYPTOGRAPHY_IS_BORINGSSL,
        CRYPTOGRAPHY_IS_AWSLC
    ))
))]
use std::ptr;

#[cfg(not(any(
    CRYPTOGRAPHY_IS_LIBRESSL,
    CRYPTOGRAPHY_IS_BORINGSSL,
    CRYPTOGRAPHY_IS_AWSLC
)))]
use openssl_sys as ffi;

#[cfg(CRYPTOGRAPHY_OPENSSL_300_OR_GREATER)]
use crate::{cvt, OpenSSLResult};

pub fn is_enabled() -> bool {
    cfg_if::cfg_if! {
        if #[cfg(any(CRYPTOGRAPHY_IS_LIBRESSL, CRYPTOGRAPHY_IS_BORINGSSL))] {
            false
        } else if #[cfg(CRYPTOGRAPHY_OPENSSL_300_OR_GREATER)] {
            // SAFETY: No pre-conditions
            unsafe {
                ffi::EVP_default_properties_is_fips_enabled(ptr::null_mut()) == 1
            }
        } else {
            openssl::fips::enabled()
        }
    }
}

#[cfg(CRYPTOGRAPHY_OPENSSL_300_OR_GREATER)]
pub fn enable() -> OpenSSLResult<()> {
    // SAFETY: No pre-conditions
    unsafe {
        cvt(ffi::EVP_default_properties_enable_fips(ptr::null_mut(), 1))?;
    }

    Ok(())
}
