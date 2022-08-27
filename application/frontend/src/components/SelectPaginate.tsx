import React from 'react';
import { AsyncPaginate, LoadOptions } from 'react-select-async-paginate';
import { components, DropdownIndicatorProps, GroupBase, MultiValue, SingleValue, StylesConfig } from 'react-select';
import { Controller, useFormContext } from 'react-hook-form';
import { Box, useTheme } from '@mui/material';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import ArrowDropUpIcon from '@mui/icons-material/ArrowDropUp';
import { ErrorMessage } from './ErrorMessage';

type Option = {
    value: string | number;
    label: string;
};

type Group = GroupBase<Option>;

type Additional = {
    page: number;
};

type IsMulti = boolean;

interface Props {
    name: string;
    label: string;
    triggerNames?: string[];
    errorName?: string;
    marginBottom?: boolean;
    marginLeft?: boolean;
    disabled?: boolean;
    width?: number;
    multi?: boolean;
    loadOptions: LoadOptions<Option, Group, Additional>;
}

const SelectPaginate: React.FC<Props> = ({
    name,
    label,
    triggerNames,
    errorName,
    marginBottom = true,
    marginLeft = true,
    disabled = false,
    width,
    multi = false,
    loadOptions,
}) => {
    if (!errorName) {
        errorName = name;
    }
    const theme = useTheme();
    const { control, trigger } = useFormContext();

    const customStyles: (isValid: boolean) => StylesConfig<Option, IsMulti> = (isValid) => ({
        option: (provided) => ({
            ...provided,
            borderRadius: theme.shape.borderRadius,
        }),
        control: (provided) => ({
            ...provided,
            // @ts-expect-error: theme (in theme.ts) has root defined as an object with height, but the type says root is string
            height: theme.components.MuiInputBase.styleOverrides.root.height,
            borderColor: isValid
                ? // @ts-expect-error: theme (in theme.ts) has root defined as an object with fieldset (and bordercolor), but the type says root is string
                  theme.components.MuiInputBase.styleOverrides.root.fieldset.borderColor
                : theme.palette.error.main,
            // TODO: When input is focues AND hovered both the outline and the border is showing, while only outline should show.
            ':hover': {
                borderColor: isValid ? theme.palette.common.black : theme.palette.error.main,
            },
        }),
        placeholder: (provided) => ({
            ...provided,
            color: isValid ? undefined : theme.palette.error.main,
        }),
        dropdownIndicator: (provided) => ({
            ...provided,
            color: theme.palette.action.active,
            ':hover': {
                backgroundColor: theme.palette.action.hover,
                borderRadius: '50%',
                padding: '2px',
                margin: '6px',
            },
        }),
    });

    const DropdownIndicator = (props: DropdownIndicatorProps<Option, boolean, GroupBase<Option>>) => {
        return (
            components.DropdownIndicator && (
                <components.DropdownIndicator {...props}>
                    {props.selectProps.menuIsOpen ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />}
                </components.DropdownIndicator>
            )
        );
    };

    const IndicatorSeparator = () => null;

    const isMultiValue = (x: any): x is MultiValue<Option> => Array.isArray(x);

    return (
        <Box
            sx={{
                marginBottom: marginBottom ? 2 : 0,
                marginLeft: marginLeft ? 2 : 0,
                display: 'flex',
                flexDirection: 'column',
                width: width ? `${width}px` : null,
            }}
        >
            <Controller
                render={({ field, formState }) => (
                    <AsyncPaginate
                        components={{ DropdownIndicator, IndicatorSeparator }}
                        styles={customStyles(!formState.errors[name])}
                        {...field}
                        placeholder={label}
                        /*error={!!formState.errors[name]}*/
                        isDisabled={disabled}
                        loadOptions={loadOptions}
                        isMulti={multi}
                        onChange={(option: MultiValue<Option> | SingleValue<Option>) => {
                            if (isMultiValue(option)) {
                                field.onChange(option);
                            } else {
                                field.onChange(option);
                            }
                            // TODO: Temporary fix to handle how yup updates the validation and check of errors
                            if (triggerNames) {
                                trigger([...triggerNames, name]);
                            }
                        }}
                        additional={{
                            page: 1,
                        }}
                    />
                )}
                name={name}
                control={control}
            />
            <ErrorMessage name={errorName} />
        </Box>
    );
};

export { SelectPaginate, Option, Group, Additional };