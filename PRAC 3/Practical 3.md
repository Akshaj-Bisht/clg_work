### Analysis of the Windows Registry


---

## Aim
> To study the Windows Registry, identify its main root keys, and understand its use in Windows configuration and forensic examination.

## Requirements
- Windows computer
- Registry Editor (`regedit`)
- Permission to examine the system

## What is the Windows Registry?
The Windows Registry is a hierarchical database used by Windows and applications to store configuration settings. It contains system-wide, user-specific, and application-related information. Registry data can help with troubleshooting, but individual entries need context and should be corroborated before drawing conclusions.

## Procedure
1. Press **Windows + R**, type `regedit`, and press **Enter**.
2. Approve the prompt if it appears.
3. In Registry Editor, expand the root keys and view the example paths shown below.
4. Select a key to view its values and data types. Do not change or delete values.
5. Record the key path and the details relevant to the practical.

![[images/3.png]]
*Registry Editor root keys from your own screenshot.*

## Main root keys
The Registry Editor displays these predefined root keys. They are logical views into registry data; they are not all separate physical hive files.

| Root key | Purpose |
| --- | --- |
| `HKEY_LOCAL_MACHINE` (`HKLM`) | System-wide configuration, including hardware, drivers, Windows settings, and installed software. |
| `HKEY_CURRENT_USER` (`HKCU`) | Settings for the currently logged-in user. It is a view associated with that user's profile under `HKEY_USERS`. |
| `HKEY_CLASSES_ROOT` (`HKCR`) | File type and COM registration information. It presents a merged view of per-user and per-machine Classes data. |
| `HKEY_USERS` (`HKU`) | Loaded user profiles, identified by security identifiers (SIDs), and related settings. |
| `HKEY_CURRENT_CONFIG` (`HKCC`) | A view of the hardware profile used for the current session. |

![[images/practical-3-001.png]]
*Example of a user-specific path under `HKEY_CURRENT_USER`.*

![[images/practical-3-002.png]]
*Example of a file extension association shown under `HKEY_CLASSES_ROOT`.*

![[images/practical-3-003.png]]
*Example of a user profile represented by a SID under `HKEY_USERS`.*

![[images/practical-3-004.png]]
*Example setting shown under `HKEY_CURRENT_CONFIG`.*

## Keys, subkeys, and values
- A **key** is a registry container, similar to a folder.
- A **subkey** is a key located inside another key.
- A **value** stores a named setting and has a data type, such as string, number, or binary data.

For example:

```text
HKEY_CURRENT_USER\Software\Microsoft
```

Here, `Software` is a subkey of `HKEY_CURRENT_USER`, and `Microsoft` is a subkey of `Software`.

![[images/1.png]]


## Conclusion
> The Windows Registry stores important system and user configuration. Careful, read-only examination can support digital forensic analysis when the source, context, and limitations of each finding are documented.

